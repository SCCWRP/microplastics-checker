import os, time, re
from flask import send_file, Blueprint, jsonify, request, g, current_app, render_template, send_from_directory, g 
from pandas import read_sql, DataFrame
import pandas as pd
from sqlalchemy import create_engine

download = Blueprint('download', __name__)
@download.route('/download/<submissionid>/<filename>', methods = ['GET','POST'])
def submission_file(submissionid, filename):
    return send_file( os.path.join(os.getcwd(), "files", submissionid, filename), as_attachment = True, download_name = filename ) \
        if os.path.exists(os.path.join(os.getcwd(), "files", submissionid, filename)) \
        else jsonify(message = "file not found")

@download.route('/export', methods = ['GET','POST'])
def template_file():

    # define the "engine" (database connection)
    eng = g.eng
    
    agencycode = request.args.get('agency')
    print("Agency code")
    print(agencycode)

    if request.args.get("agency"):

        # Make sure the query string argument is a valid agency code
        if not agencycode in pd.read_sql("SELECT DISTINCT agencycode FROM lu_agencies;", eng).agencycode.values:
            return f"Agency code {agencycode} not found!"
        
        # We know a record exists for this query in the database at this point because if there wasnt, it would have already returned above
        agency = pd.read_sql(f"SELECT agency FROM lu_agencies WHERE agencycode = '{agencycode}';", eng).agency.values[0]

        print(f'agency: {agency}')
        
        # add another folder within /export folder for returning data to user (either in browser or via excel file)
        # probably better to not store all these queries in an excel file for storage purposes - use timestamp if this is an issue
        # name after agency and table for now
        export_name = f'{agencycode}-export.xlsx'
        export_file = os.path.join(os.getcwd(), "export", "data_query", export_name)
        export_writer = pd.ExcelWriter(export_file, engine='xlsxwriter')
        

        #call database to get occupation data
        occupation_df = pd.read_sql(f"""SELECT 
                                    stationid, 
                                    date(occupationdate) as occupationdate,
                                    to_char((occupationdate-interval'7 hours'), 'HH24:MI:SS') as occupationtime,
                                    timezone as occupationtimezone,
                                    samplingorganization,
	                                collectiontype,
	                                vessel,
	                                navigationtype as navtype,
	                                salinity,
	                                salinityunits,
	                                weather,
	                                windspeed,
	                                windspeedunits,
	                                winddirection,
	                                swellheight,
                                    swellheightunits,
	                                swellperiod, 
                                    'seconds' AS swellperiodunits,
                                    swelldirection,
	                                seastate, 
	                                stationfail,
	                                abandoned,
	                                stationdepth as occupationdepth,
                                    stationdepthunits as occupationdepthunits,
	                                occupationlat as occupationlatitude, 
	                                occupationlon as occupationlongitude,
	                                datum as occupationdatum,
	                                stationcomments as comments
                                FROM mobile_occupation_trawl
                                WHERE samplingorganization = '{agency}'
                                UNION
                                SELECT
                                    stationid,
                                    date(occupationdate) as occupationdate,
                                    to_char((occupationdate-interval'7 hours'),'HH24:MI:SS') as occupationtime,
                                    timezone as occupationtimezone,
                                    samplingorganization,
                                    collectiontype,
                                    vessel,
                                    navigationtype as navtype,
                                    salinity,
                                    salinityunits,
                                    weather,
                                    windspeed,
                                    windspeedunits,
                                    winddirection,
                                    swellheight,
                                    swellheightunits,
                                    swellperiod,
                                    'seconds' AS swellperiodunits,
                                    swelldirection,
                                    seastate,
                                    stationfail,
                                    abandoned,
                                    stationdepth as occupationdepth,
                                    stationdepthunits as occupationdepthunits,
                                    occupationlat as occupationlatitude,
                                    occupationlon as occupationlongitude,
                                    datum as occupationdatum,
                                    stationcomments as comments
                                FROM
                                    mobile_occupation_grab
                                WHERE samplingorganization = '{agency}';
                            """, eng)
        print("working checkpoint")
        print("occupation_df: ")
        print(occupation_df)

        # call to database to get trawl data
        trawl_df = pd.read_sql(f""" SELECT 
                                        trawlstationid as stationid,
                                        date(trawloverdate) as sampledate,
                                        trawlsamplingorganization as samplingorganization,
                                        trawlgear as gear,
                                        trawlnumber,
                                        trawldatum as datum, 
                                        (trawloverdate-interval'7 hours')::time as overtime, 
                                        trawlovery as overlatitude, 
                                        trawloverx as overlongitude,
                                        (trawlstartdate-interval'7 hours')::time as starttime, 
                                        trawlstarty as startlatitude, 
                                        trawlstartx as startlongitude,
                                        trawlstartdepth as startdepth, 
                                        trawldepthunits as depthunits, 
                                        trawlwireout as wireout,
                                        (trawlenddate-interval'7 hours')::time as endtime, 
                                        trawlendy as endlatitude, 
                                        trawlendx as endlongitude,
                                        trawlenddepth as enddepth, 
                                        (trawldeckdate-interval'7 hours')::time as decktime, 
                                        trawldecky as decklatitude, 
                                        trawldeckx as decklongitude, 
                                        trawlfail, 
                                        ptsensor, 
                                        ptsensormanufacturer, 
                                        ptsensorserialnumber,
                                        netonbottomtemp as onbottomtemp, 
                                        netonbottomtime as onbottomtime, 
                                        COALESCE(debrisdetected, 'No') AS debrisdetected,
                                        trawlcomments as comments
                                    FROM mobile_trawl
                                    WHERE
                                        trawlsamplingorganization = '{agency}';
                                """, eng)
        print("trawl_df:")
        print(trawl_df)
        print(type(trawl_df))

        # call to database to get grab data
        grab_df = pd.read_sql(f"""SELECT
                                    grabstationid as stationid,
                                    date(grabdate) as sampledate, 
                                    to_char((grabdate-interval'7 hours'), 'HH24:MI:SS') as sampletime,
                                    grabnumber as grabeventnumber,
                                    grabsamplingorganization as samplingorganization,
                                    grabgear as gear, 
                                    grabx as latitude,
                                    graby as longitude, 
                                    grabdatum as datum, 
                                    grabstationwaterdepth as stationwaterdepth,
                                    grabstationwaterdepthunits as stationwaterdepthunits, 
                                    grabpenetration as penetration, 
                                    grabpenetrationunits as penetrationunits, 
                                    grabsedimentcomposition as composition, 
                                    grabsedimentcolor as color, 
                                    grabsedimentodor as odor, 
                                    grabshellhash as shellhash, 
                                    benthicinfauna, 
                                    sedimentchemistry, 
                                    grainsize, 
                                    toxicity, 
                                    pfas,
                                    pfasfieldblank,
                                    microplastics,
                                    microplasticsfieldblank,
                                    equipmentblank,
                                    grabfail, 
                                    COALESCE(debrisdetected, 'No') AS debrisdetected, 
                                    grabcomments as comments 
                                FROM mobile_grab
                                WHERE grabsamplingorganization = '{agency}';
                                """, eng)
        print("grab_df: ")
        print(grab_df)
        print(type(grab_df))

    
    with export_writer:
        occupation_df.to_excel(export_writer, sheet_name = "occupation", index = False)
        trawl_df.to_excel(export_writer, sheet_name = "trawl", index = False)
        grab_df.to_excel(export_writer, sheet_name = "grab", index = False)
    

    return render_template('export.html', export_name=export_name, agency=agency)


# idea is to serve export.html above, then have this route serve the exported file
# This route works with the export tool (above)
@download.route('/export/data_query/<export_name>', methods = ['GET','POST'])
def data_query(export_name):
    return send_from_directory(os.path.join(os.getcwd(), "export", "data_query"), export_name, as_attachment=True)




@download.route("/intercal-data", methods=["POST", "GET"])
def export():
    eng = create_engine(os.getenv("INTERCAL_DB_CONNECTION_STRING"))

    tablename = request.args.get("table")
    lab = request.args.get("lab")
    matrix = request.args.get("matrix")
    
    if tablename is None:
        return "Tablename not provided."

    # Double percent is needed when typing queries in python, in order to type a literal percent
    # its like an escape character so python knows you are not trying to type a format string
    if (tablename not in pd.read_sql("SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'tbl_%%';", eng).table_name.values) and (tablename != 'sample_spiking_info'):
        return "Invalid table name given"
    
    cols = pd.read_sql(
            "SELECT column_name FROM information_schema.columns WHERE table_name = '{}' AND column_name NOT IN ('{}') ".format(
                tablename, 
                "','".join(
                    set(current_app.system_fields) - {'objectid'}
                )
            ),
            eng
        ) \
        .column_name \
        .values

    sql = f"SELECT {','.join(cols)} FROM {tablename}"

    # Matrix only applies to raw data results
    if (matrix is not None) and (tablename in ('tbl_rawdataresults', 'sample_spiking_info')):
        # 4 valid matrix types: Clean Water, Dirty Water, Fish Tissue and Sediment
        if matrix.upper() in ("CW","DW","FT","SD"):
            sql = f"{sql} WHERE UPPER(sampletype) = '{matrix.upper()}'"
    
    if lab: # is not None
        if lab in pd.read_sql("SELECT DISTINCT labcode FROM lu_laboratories;", eng).labcode.values:
            if "WHERE" in sql:
                sql = f"{sql} AND UPPER(labid) = '{lab.upper()}'"
            else:
                sql = f"{sql} WHERE UPPER(labid) = '{lab.upper()}'"

    # Tack on the semicolon just because
    sql = f"{sql};"

    # write this to csv somewhere and return send_file of that file you just wrote
    path = f"{os.getcwd()}/export/{tablename}.csv"
    data = pd.read_sql(sql, eng)
    
    lab_anonymizer = pd.read_sql("SELECT labcode, anonymous_labcode FROM lab_anonymizer;", eng)

    if (str(request.args.get("anonymize")).lower() == 'false') or (tablename == 'sample_spiking_info'):
        print("We will give unanonymized data")
    else:
        for col in data.columns:
            if col not in ('labid','sampleid','particleid','photoid'):
                continue
            for old, new in zip(lab_anonymizer.labcode, lab_anonymizer.anonymous_labcode):
                data[col] = data[col].str.replace(old,f'Lab{new}')

    data.to_csv(path, index = False)


    return send_file(path, as_attachment=True, download_name=f'{tablename}.csv')
    