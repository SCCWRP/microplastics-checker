import os, re
import pandas as pd
from bs4 import BeautifulSoup
from io import BytesIO
from flask import Blueprint, g, current_app, render_template, redirect, url_for, session, request, jsonify, send_file, flash, abort
import psycopg2
from psycopg2 import sql

from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import time
from werkzeug.utils import secure_filename
from zipfile import ZipFile



from .utils.db import metadata_summary
from .utils.generic import allowed_imagefile

photoviewer = Blueprint('photoviewer', __name__)

@photoviewer.route('/particleviewer')
def index():
    particleid = request.args.get('particleid')

    if particleid is None:
        # ParticleID not found in the query string arguments
        return render_template('particle-search.jinja2', AUTHORIZED = session.get('AUTHORIZED_FOR_ADMIN_FUNCTIONS'))
    
    # prevent sql injection
    particleid = str(particleid).replace("'","").replace('"','').replace(';','')
    
    sql = "SELECT particleid, morphology, color, photoid, lab, sampletype, stationid, submissionid FROM tbl_mp_results WHERE particleid ~ %s;"
    data = pd.read_sql(sql, g.eng, params=(particleid,))


    if len(data) == 1:
        # In this case, we found one particle
        # Here we display that particle's photo along with information of the other particles which are found in that photo
        photoid = data.photoid.tolist()[0].replace("'","").replace('"','').replace(';','')
        data = pd.read_sql(
            f"SELECT particleid, morphology, color, photoid, lab, sampletype, stationid, submissionid FROM tbl_mp_results WHERE photoid = '{photoid}';", 
            g.eng
        )
        return render_template('particle-photo-display.jinja2', data = data.to_dict('records'), current_particle = particleid, AUTHORIZED = session.get('AUTHORIZED_FOR_ADMIN_FUNCTIONS'))

    elif len(data) > 1:
        # Display a table with info for each particle found in the search result
        # rows of table should link to the corresponding particle-photo-display template (which is this same route) 
        #   This should be accomplished by having an href with the particleid in the query string
        return render_template('particle-search-results-table.jinja2', data = data.to_dict('records'), particle_search_query = particleid, AUTHORIZED = session.get('AUTHORIZED_FOR_ADMIN_FUNCTIONS'))

    else:
        # This is the case where we got an empty dataframe
        # This means no particles were found in the search results
        flash(f"No search result found for particle: {particleid}")
        return render_template('particle-search.jinja2', AUTHORIZED = session.get('AUTHORIZED_FOR_ADMIN_FUNCTIONS'))



@photoviewer.route('/photos/<photoid>')
def get_photo(photoid):
    photoid = str(photoid).replace('"','').replace("'","").replace(';','')
    data = pd.read_sql(f"SELECT DISTINCT submissionid, photoid FROM tbl_mp_results WHERE photoid = '{photoid}';", g.eng)

    if len(data) > 0:
        submissionid = data.submissionid.values[0]
        photopath = os.path.join(os.getcwd(), 'images', str(submissionid), photoid)
        if os.path.exists(photopath):
            return send_file(photopath)
    
    abort(404)




@photoviewer.route('/particle-auth', methods = ['GET','POST'])
def auth():

    adminpw = request.form.get('adminpw')
    if adminpw == os.environ.get("ADMIN_FUNCTION_PASSWORD"):
        session['AUTHORIZED_FOR_ADMIN_FUNCTIONS'] = True
        

    return jsonify( success=(session.get("AUTHORIZED_FOR_ADMIN_FUNCTIONS") == True) )


# I know technically this route isnt for viewing photos, but i decided to attach to this blueprint since it is most closely related
# Later maybe i'll change the blueprint name
@photoviewer.route('/photoupload', methods=['GET','POST'])
def photoupload():

    if session.get('submission_photos_dir', None) is None:
        ACTIVE_SESSION = False
    else:
        ACTIVE_SESSION = True

    if request.method == 'POST':
        files = request.files.getlist('file')
        if not files or len(files) == 0:
            flash('No file selected!', 'error')
            return redirect(request.url)

        save_path = session.get('submission_photos_dir')

        for file in files:
            if file and allowed_imagefile(file.filename):
                filename = secure_filename(file.filename)
                if filename.rsplit('.', 1)[1].lower() == 'zip':
                    with ZipFile(file) as zipf:
                        zipf.extractall(path=save_path)
                else:
                    file.save(os.path.join(save_path, filename))
            else:
                # flash(f"Invalid file type: {file.filename}", 'error')
                return "Please upload png or jpg", 415
        flash('Files uploaded successfully!', 'success')
        return redirect(url_for('photoviewer.photoupload'))

    return render_template('photoupload.jinja2',ACTIVE_SESSION=ACTIVE_SESSION)

    

