# Dont touch this file! This is intended to be a template for implementing new custom checks
from inspect import currentframe
from flask import current_app, g, session
from datetime import datetime
from .functions import checkData, mismatch
import pandas as pd
import numpy as np
import os, re

def microplastics(all_dfs):
    
    current_function_name = str(currentframe().f_code.co_name)
    
    # function should be named after the dataset in app.datasets in __init__.py
    assert current_function_name in current_app.datasets.keys(), \
        f"function {current_function_name} not found in current_app.datasets.keys() - naming convention not followed"

    expectedtables = set(current_app.datasets.get(current_function_name).get('tables'))
    assert expectedtables.issubset(set(all_dfs.keys())), \
        f"""In function {current_function_name} - {expectedtables - set(all_dfs.keys())} not found in keys of all_dfs ({','.join(all_dfs.keys())})"""


    
    
    
    # Begin Microplastics Custom Checks
    print("# --- Begin Microplastics Custom Checks --- #")




    # define errors and warnings list
    errs = []
    warnings = []

    # since often times checks are done by merging tables (Paul calls those logic checks)
    # we assign dataframes of all_dfs to variables and go from there
    # This is the convention that was followed in the old checker
    
    # ------

    # Makes sure each variable is an empty dataframe if not found in all_dfs
    labinfo = all_dfs.get('tbl_mp_labinfo', pd.DataFrame())
    instrumentinfo = all_dfs.get('tbl_mp_instrumentinfo', pd.DataFrame())
    microscopy = all_dfs.get('tbl_mp_microscopysettings', pd.DataFrame())
    raman = all_dfs.get('tbl_mp_ramansettings', pd.DataFrame())
    ftir = all_dfs.get('tbl_mp_ftirsettings', pd.DataFrame())
    results = all_dfs.get('tbl_mp_results', pd.DataFrame())
    sampleextraction = all_dfs.get('tbl_mp_sampleextraction', pd.DataFrame())
    samplereceiving = all_dfs.get('tbl_mp_samplereceiving', pd.DataFrame())

    labinfo['tmp_row'] = labinfo.index
    instrumentinfo['tmp_row'] = instrumentinfo.index
    microscopy['tmp_row'] = microscopy.index
    raman['tmp_row'] = raman.index
    ftir['tmp_row'] = ftir.index
    results['tmp_row'] = results.index
    sampleextraction['tmp_row'] = sampleextraction.index
    samplereceiving['tmp_row'] = samplereceiving.index

    args = {
        "tablename": "",
        "badrows": [],
        "badcolumn": "",
        "error_type": "",
        "is_core_error": False,
        "error_message": ""
    }



    ######################################################################################################################
    # ------------------------------------------------------------------------------------------------------------------ #
    # ------------------------------------------------  Logic Checks --------------------------------------------------- #
    # ------------------------------------------------------------------------------------------------------------------ #
    ######################################################################################################################





    # --------------------------- Photo Logic Checks ------------------------------- #

    print("# CHECK - PhotoID of tbl_mp_results tab must have a matching uploaded photo ")
    # Description: PhotoID of tbl_mp_results tab must have a matching uploaded photo (🛑 ERROR 🛑)
    # Created Coder: Nick Lombardo
    # Created Date: 08/21/23
    # Last Edited Date: 9/1/2023
    # Last Edited Coder: Robert Butler
    # NOTE (09/01/2023): Photos no longer required if the PolymerID says 'Not measured'

    uploaded_photoids = os.listdir(session['submission_photos_dir'])

    errs = [
        *errs,
        checkData(
            tablename = "tbl_mp_results",
            badrows = results[
                # Get records where the photoid was not left blank...
                (results.photoid.fillna('').astype(str).str.replace("\s*","", regex = True) != '')
                &
                # AND the photoID was not found in the uploaded photos directory
                (~results['photoid'].isin(uploaded_photoids))
            ].tmp_row.tolist(), 
            badcolumn = "PhotoID",
            error_type = "Logic Error",
            error_message = "PhotoID of mp_results tab must have a matching uploaded photo. If there is not photo for the particle, you may leave the cell empty."
        )
    ]

    # END OF CHECK - PhotoID of tbl_mp_results tab must have a matching uploaded photo (🛑 ERROR 🛑)
    print("# END OF CHECK - PhotoID of tbl_mp_results tab must have a matching uploaded photo")


    print("# CHECK - PhotoID required only for records where the polymerID is not 'Not measured' ")
    # Description: PhotoID required only for records where the polymerID is not 'Not measured' (🛑 ERROR 🛑)
    # Created Coder: Robert Butler
    # Created Date: 9/1/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    errs = [
        *errs,
        checkData(
            tablename = "tbl_mp_results",
            badrows = results[
                # Get records where PolymerID is NOT 'Not measured'
                (results.polymerid.astype(str).str.lower() != 'not measured') 
                # But the photoid was left blank...
                & (results.photoid.fillna('').astype(str).str.replace("\s*","", regex = True) == '')
            ].tmp_row.tolist(), 
            badcolumn = "PhotoID",
            error_type = "Logic Error",
            error_message = "Photos are required for records where there is a PolymerID (even if the polymer was not able to be identified)"
        )
    ]

    # END OF CHECK - PhotoID required only for records where the polymerID is not 'Not measured' (🛑 ERROR 🛑)
    print("# END OF CHECK - PhotoID required only for records where the polymerID is not 'Not measured'")


    print("# CHECK - Photo uploaded must match their submission (PhotoID column in the tbl_mp_results tab)")
    # Description: Photo uploaded must match their submission (PhotoID column in the tbl_mp_results tab) (🛑 ERROR 🛑)
    # Created Coder: Nick Lombardo
    # Created Date: 08/22/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    # print("all photo uploads isin results['photoid']")
    # print(pd.Series(uploaded_photoids))
    # print(results['photoid'])
    # print(pd.Series(uploaded_photoids).isin(results['photoid']))
    if not pd.Series(uploaded_photoids).isin(results['photoid']).all():
        errs = [
            *errs,
            checkData(
                tablename = "tbl_mp_results",
                badrows = results.tmp_row.tolist(), 
                badcolumn = "PhotoID",
                error_type = "Logic Error",
                error_message = "All uploaded photos must have a matching PhotoID in mp_results tab"
            )
        ]


    # END OF CHECK - Photo uploaded must match their submission (PhotoID column in the tbl_mp_results tab) (🛑 ERROR 🛑)
    print("# END OF CHECK - Photo uploaded must match their submission (PhotoID column in the tbl_mp_results tab)")


    print("# CHECK - Cannot upload a photo with a filename that matches one that was previously used in a previous submission")
    # Description - Cannot upload a photo with a filename that matches one that was previously used in a previous submission (🛑 ERROR 🛑)
    # Created Coder: Nick Lombardo
    # Created Date: 08/22/23
    # Last Edited Date: 8/29/2023
    # Last Edited Coder: Robert Butler
    # NOTE (08/29/2023): Put .photoid at the end of query that gets the previously used photoids

    unique_photoids = pd.read_sql('SELECT DISTINCT photoid from tbl_mp_results', g.eng).photoid

    errs = [
        *errs,
        checkData(
            tablename = "tbl_mp_results",
            badrows = results[results['photoid'].isin(unique_photoids)].tmp_row.tolist(), 
            badcolumn = "PhotoID",
            error_type = "Logic Error",
            error_message = "This PhotoID was used in a previous submission, please use a different file name."
        )
    ]

    # END OF CHECK - Cannot upload a photo with a filename that matches on that was previously used in a previous submission (🛑 ERROR 🛑)
    print("# END OF CHECK - Cannot upload a photo with a filename that matches on that was previously used in a previous submission")

    # --------------------------- END Photo Logic Checks --------------------------- #





    # ---------------------------------------------------------------------------------------------------- #
    # ------------------ Traditional Logic Checks: Checking relationships between tables ----------------- #
    # ---------------------------------------------------------------------------------------------------- #



    # ------------------------------- BEGIN Relating Results tab to the other tables --------------------------- #


    # ------- Results <-----> Settings tables ------- #

    print("# CHECK - If Raman = 'Yes' (in results table) then there must be a corresponding record in the ramansettings table ")
    # Description - If Raman = 'Yes' (in results table) then there must be a corresponding record in the ramansettings table 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    # Created Coder: Nick Lombardo
    # Created Date: 08/21/23
    # Last Edited Date: 08/30/23
    # Last Edited Coder: Robert Butler
    # NOTE (08/24/23): Updated to use the generic mismatch function instead
    # NOTE (08/28/23): Removed if block since mismatch function handles empty dataframes already
    # NOTE (08/30/23): Updated the value of the "badcolumn" arg to be the columns that the dataframs match on

    
    errs = [
        *errs,
        checkData(
            tablename = "tbl_mp_results",
            badrows = mismatch(
                df1 = results[results['raman'] == 'Yes'],
                df2 = raman,
                mergecols = ['stationid', 'sampledate', 'lab', 'matrix', 'sampletype', 'sizefraction', 'labbatch', 'fieldreplicate']
            ), 
            badcolumn = "StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction, LabBatch, FieldReplicate",
            error_type = "Logic Error",
            error_message = "There must be a corresponding record in the ramansettings table"
        )
    ]

    # added 8/25/2023 by Robert
    errs = [
        *errs,
        checkData(
            tablename = "tbl_mp_ramansettings",
            badrows = mismatch(
                df2 = raman,
                df1 = results[results['raman'] == 'Yes'],
                mergecols = ['stationid', 'sampledate', 'lab', 'matrix', 'sampletype', 'sizefraction', 'labbatch', 'fieldreplicate']
            ), 
            badcolumn = "StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction, LabBatch, FieldReplicate",
            error_type = "Logic Error",
            error_message = "There must be a corresponding record in the ramansettings table"
        )
    ]


    # END OF CHECK - If Raman = 'Yes' (in results table) then there must be a corresponding record in the ramansettings table 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    print("# END OF CHECK - If Raman = 'Yes' (in results table) then there must be a corresponding record in the ramansettings table ")



    print("# CHECK - If FTIR = 'Yes' (in results table) then there must be a corresponding record in the ftirsettings table ")
    # CHECK - If FTIR = 'Yes' (in results table) then there must be a corresponding record in the ftirsettings table 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    # Created Coder: Nick Lombardo
    # Created Date: 08/21/23
    # Last Edited Date: 08/30/2023
    # Last Edited Coder: Robert Butler
    # NOTE (8/25/2023): Added LabBatch and FieldRep to the columns that the dataframes match on - Robert
    # NOTE (8/25/2023): remove the other direction of the logic check from the if block, since we will always want to check that - Robert
    # NOTE (08/28/23): Removed if block since mismatch function handles empty dataframes already
    # NOTE (08/30/23): put the columns to match on in a variable called matchcols (Robert)

    matchcols = ['stationid', 'sampledate', 'lab', 'matrix', 'sampletype', 'sizefraction', 'labbatch', 'fieldreplicate']
    errs = [
        *errs,
        checkData(
            tablename = "tbl_mp_results",
            badrows = mismatch(
                df1 = results[results['ftir'] == 'Yes'],
                df2 = ftir,
                mergecols = matchcols
            ), 
            badcolumn = ','.join(matchcols),
            error_type = "Logic Error",
            error_message = "There must be a corresponding record in the ftirsettings table"
        )
    ]

    # unindented from if block on 8/25/2023
    errs = [
        *errs,
        checkData(
            tablename = "tbl_mp_ftirsettings",
            badrows = mismatch(
                df1 = ftir,
                df2 = results[results['ftir'] == 'Yes'],
                mergecols = matchcols
            ), 
            badcolumn = ','.join(matchcols),
            error_type = "Logic Error",
            error_message = "There must be a corresponding record in the results table"
        )
    ]


    # END OF CHECK - If FTIR = 'Yes' (in results table) then there must be a corresponding record in the ftirsettings table 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    print("# END OF CHECK - If FTIR = 'Yes' (in results table) then there must be a corresponding record in the ftirsettings table ")
    



    print("# CHECK - If stereoscope = 'Yes' (in results table) then there must be a corresponding record in the microscopysettings table ")
    # CHECK - If stereoscope = 'Yes' (in results table) then there must be a corresponding record in the microscopysettings table 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    # Created Coder: Nick Lombardo
    # Created Date: 08/21/23
    # Last Edited Date: 08/30/2023
    # Last Edited Coder: Robert Butler
    # NOTE (08/25/23): Added LabBatch and FieldRep to the columns that the dataframes match on
    # NOTE (08/28/23): Removed if block since mismatch function handles empty dataframes already
    # NOTE (08/30/23): put the columns to match on in a variable called matchcols (Robert)

    matchcols = ['stationid', 'sampledate', 'lab', 'matrix', 'sampletype', 'sizefraction', 'labbatch', 'fieldreplicate']
    errs = [
        *errs,
        checkData(
            tablename = "tbl_mp_results",
            badrows = mismatch(
                df1 = results[results['stereoscope'] == 'Yes'],
                df2 = microscopy,
                mergecols = matchcols
            ), 
            badcolumn = ",".join(matchcols),
            error_type = "Logic Error",
            error_message = "There must be a corresponding record in the microscopysettings table"
        )
    ]

    # unindented from the if block on 8/25/2023 by Robert Butler
    errs = [
        *errs,
        checkData(
            tablename = "tbl_mp_microscopysettings",
            badrows = mismatch(
                df1 = microscopy,
                df2 = results[results['stereoscope'] == 'Yes'],
                mergecols = matchcols
            ), 
            badcolumn = ",".join(matchcols),
            error_type = "Logic Error",
            error_message = "There must be a corresponding record in the results table"
        )
    ]


    # END OF CHECK - If stereoscope = 'Yes' (in results table) then there must be a corresponding record in the microscopysettings table 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    print("# END OF CHECK - If stereoscope = 'Yes' (in results table) then there must be a corresponding record in the microscopysettings table") 
    
    
    
    # -------END Results <-----> Settings tables ------- #




    # ------- Results <-----> InstrumentInfo ------- #

    print("""# CHECKS - for each "instrument" column which says "Yes" in the results table, there must be a corresponding instrumentinfo record """)
    # CHECKS - for each "instrument" column which says "Yes" in the results table, there must be a corresponding instrumentinfo record 
    #   (e.g. If Raman = "Yes" then...
    #           there must be a matching record in instrumentinfo where instrumenttype = 'Raman' which matches the record in the results table. 
    
    #   The matching should be done on lab and matrix
    # (🛑 ERROR 🛑)
    # Created Coder: Robert Butler
    # Created Date: 08/24/23
    # Last Edited Date: 08/28/23
    # Last Edited Coder: Nick Lombardo
    # NOTE (MM/DD/YY): NA

    print('# Get existing instrumentinfo records for the lab(s) that are being submitted')
    # Get existing instrumentinfo records for the lab(s) that are being submitted
    # There shouldnt be more than one lab in a submission but technically there can be
    # 08/28/23 changed tuple cast to joined list because tuple() returns something like ('value1',) when
    #   there's only one value in labinfo.lab.astype(str), which is a syntax error in SQL
    instrumentinfo_db = pd.read_sql(
        f"""SELECT * FROM tbl_mp_instrumentinfo WHERE lab IN ('{','.join(labinfo.lab.astype(str).tolist())}')""", 
        g.eng
    )
    
    print('# Drop columns not in the instrument info tab - such as login_, submissionid, etc')
    # Drop columns not in the instrument info tab - such as login_, submissionid, etc
    instrumentinfo_db.drop( list(set(instrumentinfo_db.columns) - set(instrumentinfo.columns)) , axis = 'columns', inplace = True)

    # Only column in instrumentinfo that isnt in the database should be tmp_row
    instrumentinfo_db['tmp_row'] = instrumentinfo_db.index
    
    print('# Concat with the submission dataframe instrument info')
    # Concat with the submission dataframe instrument info
    # NOTE this may be used in later parts of this script as well, so i make it an uppercase 
    #   so those who read the code later on can see its almost like a global
    INSTRUMENTINFO_COMBINED = pd.concat([instrumentinfo, instrumentinfo_db], ignore_index=True)

    # Raman
    # Created Coder: Robert Butler
    # Created Date: 08/24/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    print("# Raman")
    args.update({
        "tablename": "tbl_mp_results",
        # 'Yes' and 'Raman' come from lookup list values so the capitalization will match
        # It is unlikely that the lookup list values will change
        "badrows": mismatch(
            results[results.raman == 'Yes'], 
            INSTRUMENTINFO_COMBINED[INSTRUMENTINFO_COMBINED.instrumenttype == 'Raman'], 
            mergecols = ['lab', 'matrix']
        ), 
        "badcolumn": "Raman",
        "error_type": "Logic Error",
        "error_message": """For each record in the "Results" tab where the 'Raman' column says 'Yes', there must be a matching record in the "Instrument Info" tab where the 'InstrumentType' is 'Raman'. Records are matched based on 'lab' and 'matrix'."""
    })
    errs = [*errs, checkData(**args)]

    # check the other direction
    args.update({
        "tablename": "tbl_mp_instrumentinfo",
        # 'Yes' and 'Raman' come from lookup list values so the capitalization will match
        "badrows": mismatch(
            instrumentinfo[instrumentinfo.instrumenttype == 'Raman'], 
            results[results.raman == 'Yes'], 
            mergecols = ['lab', 'matrix']
        ), 
        "badcolumn": "InstrumentType",
        "error_type": "Logic Error",
        "error_message": """For each record in the "InstrumentInfo" tab where the 'InstrumentType' is 'Raman', there must be a matching record in the "Results" tab where the 'Raman' column says 'Yes'. Records are matched based on 'lab' and 'matrix'."""
    })
    errs = [*errs, checkData(**args)]

    # FTIR -------------------------
    # Created Coder: Robert Butler
    # Created Date: 08/24/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    print("# FTIR")
    args.update({
        "tablename": "tbl_mp_results",
        # 'Yes' and 'FTIR' come from lookup list values so the capitalization will match
        "badrows": mismatch(
            results[results.ftir == 'Yes'], 
            INSTRUMENTINFO_COMBINED[INSTRUMENTINFO_COMBINED.instrumenttype == 'FTIR'], 
            mergecols = ['lab', 'matrix']
        ), 
        "badcolumn": "FTIR",
        "error_type": "Logic Error",
        "error_message": """For each record in the "Results" tab where the 'FTIR' column says 'Yes', there must be a matching record in the "Instrument Info" tab where the 'InstrumentType' is 'FTIR'. Records are matched based on 'lab' and 'matrix'."""
    })
    errs = [*errs, checkData(**args)]

    # check the other direction
    args.update({
        "tablename": "tbl_mp_instrumentinfo",
        # 'Yes' and 'FTIR' come from lookup list values so the capitalization will match
        "badrows": mismatch(
            instrumentinfo[instrumentinfo.instrumenttype == 'FTIR'], 
            results[results.ftir == 'Yes'], 
            mergecols = ['lab', 'matrix']
        ), 
        "badcolumn": "InstrumentType",
        "error_type": "Logic Error",
        "error_message": """For each record in the "InstrumentInfo" tab where the 'InstrumentType' is 'FTIR', there must be a matching record in the "Results" tab where the 'FTIR' column says 'Yes'. Records are matched based on 'lab' and 'matrix'."""
    })
    errs = [*errs, checkData(**args)]



    # Stereoscope ------------------------------
    # Created Coder: Robert Butler
    # Created Date: 08/24/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    print("# Stereoscope")
    args.update({
        "tablename": "tbl_mp_results",
        # 'Yes' and 'Stereoscope' come from lookup list values so the capitalization will match
        "badrows": mismatch(
            results[results.stereoscope == 'Yes'], 
            INSTRUMENTINFO_COMBINED[INSTRUMENTINFO_COMBINED.instrumenttype == 'Stereoscope'], 
            mergecols = ['lab', 'matrix']
        ), 
        "badcolumn": "Stereoscope",
        "error_type": "Logic Error",
        "error_message": """For each record in the "Results" tab where the 'Stereoscope' column says 'Yes', there must be a matching record in the "Instrument Info" tab where the 'InstrumentType' is 'Stereoscope'. Records are matched based on 'lab' and 'matrix'."""
    })
    errs = [*errs, checkData(**args)]

    # check the other direction
    args.update({
        "tablename": "tbl_mp_instrumentinfo",
        # 'Yes' and 'Stereoscope' come from lookup list values so the capitalization will match
        "badrows": mismatch(
            instrumentinfo[instrumentinfo.instrumenttype == 'Stereoscope'], 
            results[results.stereoscope == 'Yes'], 
            mergecols = ['lab', 'matrix']
        ), 
        "badcolumn": "InstrumentType",
        "error_type": "Logic Error",
        "error_message": """For each record in the "InstrumentInfo" tab where the 'InstrumentType' is 'Stereoscope', there must be a matching record in the "Results" tab where the 'Stereoscope' column says 'Yes'. Records are matched based on 'lab' and 'matrix'."""
    })
    errs = [*errs, checkData(**args)]



    # Other --------------------
    # Created Coder: Robert Butler
    # Created Date: 08/24/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    print("# Other")
    args.update({
        "tablename": "tbl_mp_results",
        # 'Yes' and 'Other' come from lookup list values so the capitalization will match
        "badrows": mismatch(
            results[results.other_instrument_used == 'Yes'], 
            INSTRUMENTINFO_COMBINED[INSTRUMENTINFO_COMBINED.instrumenttype == 'Other'], 
            mergecols = ['lab', 'matrix']
        ), 
        "badcolumn": "other_instrument_used",
        "error_type": "Logic Error",
        "error_message": """For each record in the "Results" tab where the 'other_instrument_used' column says 'Yes', there must be a matching record in the "Instrument Info" tab where the 'InstrumentType' is 'Other'. Records are matched based on 'lab' and 'matrix'."""
    })
    errs = [*errs, checkData(**args)]

    # check the other direction
    args.update({
        "tablename": "tbl_mp_instrumentinfo",
        # 'Yes' and 'Other' come from lookup list values so the capitalization will match
        "badrows": mismatch(
            instrumentinfo[instrumentinfo.instrumenttype == 'Other'], 
            results[results.other_instrument_used == 'Yes'], 
            mergecols = ['lab', 'matrix']
        ), 
        "badcolumn": "InstrumentType",
        "error_type": "Logic Error",
        "error_message": """For each record in the "InstrumentInfo" tab where the 'InstrumentType' is 'Other', there must be a matching record in the "Results" tab where the 'other_instrument_used' column says 'Yes'. Records are matched based on 'lab' and 'matrix'."""
    })
    errs = [*errs, checkData(**args)]

    # END OF CHECKS - for each "instrument" column which says "Yes" in the results table, there must be a corresponding instrumentinfo record 
    #   (e.g. If Raman = "Yes" then...
    #           there must be a matching record in instrumentinfo where instrumenttype = 'Raman' which matches the record in the results table. 
    # (🛑 ERROR 🛑)
    print("""# END OF CHECKS - for each "instrument" column which says "Yes" in the results table, there must be a corresponding instrumentinfo record """)

    
    
    # ------- END OF Results <-----> InstrumentInfo ------- #




    # ------- Results <-----> SampleExtraction ------- #
    
    print("# CHECKS - Each record in Results must have a matching record in SampleExtraction (and vice versa)")
    # CHECKS - Each record in Results must have a matching record in SampleExtraction (and vice versa)
    #   Results Table matches SampleExtraction on  StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction, LabBatch, FieldReplicate
    # (🛑 ERROR 🛑)
    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_results",
        "badrows": mismatch(
            results, 
            sampleextraction, 
            mergecols = ['stationid', 'sampledate', 'lab', 'matrix', 'sampletype', 'sizefraction', 'labbatch', 'fieldreplicate']
        ), 
        "badcolumn": "StationID,SampleDate,Lab,Matrix,SampleType,SizeFraction,LabBatch,FieldReplicate",
        "error_type": "Logic Error",
        "error_message": "Each record in Results must have a matching record in sampleextraction. Records are matched on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction, LabBatch, FieldReplicate"
    })
    errs = [*errs, checkData(**args)]

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_sampleextraction",
        "badrows": mismatch(
            sampleextraction, 
            results, 
            mergecols = ['stationid', 'sampledate', 'lab', 'matrix', 'sampletype', 'sizefraction', 'labbatch', 'fieldreplicate']
        ), 
        "badcolumn": "StationID,SampleDate,Lab,Matrix,SampleType,SizeFraction,LabBatch,FieldReplicate",
        "error_type": "Logic Error",
        "error_message": "Each record in SampleExtraction must have a matching record in Results. Records are matched on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction, LabBatch, FieldReplicate"
    })
    errs = [*errs, checkData(**args)]
    
    # END CHECKS - Each record in Results must have a matching record in SampleExtraction (and vice versa)
    #   Results Table matches SampleExtraction on  StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction, LabBatch, FieldReplicate
    # (🛑 ERROR 🛑)
    print("# END OF CHECKS - Each record in Results must have a matching record in SampleExtraction (and vice versa)")
    
    # ------- END Results <-----> SampleExtraction ------- #




    # ------- Results <-----> SampleReceiving ------- #
    
    print("# CHECKS - Each record in Results must have a matching record in SampleReceiving (and vice versa)")
    # CHECKS - Each record in Results must have a matching record in SampleReceiving (and vice versa)
    #   Results Table matches SampleReceiving on  StationID, SampleDate, Lab, Matrix, SampleType, FieldReplicate
    # (🛑 ERROR 🛑)

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: 08/28/23
    # Last Edited Coder: Nick Lombardo
    # NOTE (08/28/23): Corrected mergecols to remove Sizefraction as one of the merge cols, since 
    #                   it's not in the SampleReceiving tab
    args.update({
        "tablename": "tbl_mp_results",
        "badrows": mismatch(
            results, 
            samplereceiving, 
            mergecols = ['stationid', 'sampledate', 'lab', 'matrix', 'sampletype', 'fieldreplicate']
        ), 
        "badcolumn": "StationID,SampleDate,Lab,Matrix,SampleType,FieldReplicate",
        "error_type": "Logic Error",
        "error_message": "Each record in Results must have a matching record in SampleReceiving. Records are matched on StationID, SampleDate, Lab, Matrix, SampleType, FieldReplicate"
    })
    errs = [*errs, checkData(**args)]

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: 08/28/23
    # Last Edited Coder: Nick Lombardo
    # NOTE (08/28/23): Corrected mergecols to remove Sizefraction as one of the merge cols, since 
    #                   it's not in the SampleReceiving tab
    args.update({
        "tablename": "tbl_mp_samplereceiving",
        "badrows": mismatch(
            samplereceiving, 
            results, 
            mergecols = ['stationid', 'sampledate', 'lab', 'matrix', 'sampletype', 'fieldreplicate']
        ), 
        "badcolumn": "StationID,SampleDate,Lab,Matrix,SampleType,FieldReplicate",
        "error_type": "Logic Error",
        "error_message": "Each record in SampleReceiving must have a matching record in Results. Records are matched on StationID, SampleDate, Lab, Matrix, SampleType, FieldReplicate"
    })
    errs = [*errs, checkData(**args)]

    # END CHECKS - Each record in Results must have a matching record in SampleReceiving (and vice versa)
    #   Results Table matches SampleReceiving on  StationID, SampleDate, Lab, Matrix, SampleType, FieldReplicate
    # (🛑 ERROR 🛑)
    print("# END CHECKS - Each record in Results must have a matching record in SampleReceiving (and vice versa)")
    
    # ------- END Results <-----> SampleReceiving ------- #




    # ------- Results <-----> LabInfo ------- #

    print("# CHECKS - Results Table matches Labinfo on StationID, SampleDate, Lab, Matrix, LabBatch, FieldReplicate (two ways)")
    # CHECKS - Results Table matches Labinfo on StationID, SampleDate, Lab, Matrix, LabBatch, FieldReplicate (two ways) (🛑 ERROR 🛑)

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_results",
        "badrows": mismatch(
            results, 
            labinfo, 
            mergecols = ['stationid', 'sampledate', 'lab', 'matrix', 'labbatch', 'fieldreplicate']
        ), 
        "badcolumn": "StationID,SampleDate,Lab,Matrix,LabBatch,FieldReplicate",
        "error_type": "Logic Error",
        "error_message": "Each record in Results must have a matching record in LabInfo. Records are matched on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction, FieldReplicate"
    })
    errs = [*errs, checkData(**args)]

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_labinfo",
        "badrows": mismatch(
            labinfo, 
            results, 
            mergecols = ['stationid', 'sampledate', 'lab', 'matrix', 'labbatch', 'fieldreplicate']
        ), 
        "badcolumn": "StationID,SampleDate,Lab,Matrix,LabBatch,FieldReplicate",
        "error_type": "Logic Error",
        "error_message": "Each record in LabInfo must have a matching record in Results. Records are matched on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction, FieldReplicate"
    })
    errs = [*errs, checkData(**args)]

    # END CHECKS - Results Table matches Labinfo on StationID, SampleDate, Lab, Matrix, LabBatch, FieldReplicate (two ways) (🛑 ERROR 🛑)
    print("# END CHECKS - Results Table matches Labinfo on StationID, SampleDate, Lab, Matrix, LabBatch, FieldReplicate (two ways)")

    # ------- END Results <-----> LabInfo ------- #


    # ----------------------------- END Relating Results tab to the other tables ------------------------- #
    


    ############################################################################################################################################





    
    
    # ------------------------------- BEGIN Relating InstrumentInfo tab to the other tables --------------------------- #

    # ------- InstrumentInfo <-----> Settings tables ------- #


    print("# CHECK - If InstrumentType = 'Raman' (in instrumentinfo table) then there must be a corresponding record in the ramansettings table") 
    # CHECK - If InstrumentType = 'Raman' (in instrumentinfo table) then there must be a corresponding record in the ramansettings table 
    #   Records must match on Lab, Matrix
    # (🛑 ERROR 🛑)

    # to match instrumentinfo to other tables
    instinfomatchcols = ['Lab','Matrix']
    
    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_instrumentinfo",
        "badrows": mismatch(
            instrumentinfo[instrumentinfo.instrumenttype == 'Raman'], 
            raman, 
            mergecols = [x.lower() for x in instinfomatchcols]
        ), 
        "badcolumn": ','.join(instinfomatchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in Instrumentinfo (where instrumenttype = Raman) must have a matching record in RamanSettings. Records are matched on {', '.join(instinfomatchcols)}"
    })
    errs = [*errs, checkData(**args)]

    
    # END OF CHECK - If InstrumentType = 'Raman' (in instrumentinfo table) then there must be a corresponding record in the ramansettings table 
    #   Records must match on Lab, Matrix
    # (🛑 ERROR 🛑)
    print("# END OF CHECK - If InstrumentType = 'Raman' (in instrumentinfo table) then there must be a corresponding record in the ramansettings table")



    print("# CHECK - Record in ramansettings requires a corresponding record in InstrumentInfo where InstrumentType = 'Raman'")
    # CHECK - Record in ramansettings requires a corresponding record in InstrumentInfo where InstrumentType = 'Raman' 
    #   Records must match on Lab, Matrix
    # (🛑 ERROR 🛑)
    
    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    # NOTE:
    # No error if there is an existing record in the database, so we use the INSTUMENTINFO_COMBINED dataframe defined earlier in the script
    
    args.update({
        "tablename": "tbl_mp_ramansettings",
        "badrows": mismatch(
            raman, 
            INSTRUMENTINFO_COMBINED[INSTRUMENTINFO_COMBINED.instrumenttype == 'Raman'], 
            mergecols = [x.lower() for x in instinfomatchcols]
        ), 
        "badcolumn": ','.join(instinfomatchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in RamanSettings must have a matching record in Instrumentinfo (where instrumenttype = Raman). Records are matched on {', '.join(instinfomatchcols)}"
    })
    errs = [*errs, checkData(**args)]
    
    # END CHECK - Record in ramansettings requires a corresponding record in InstrumentInfo where InstrumentType = 'Raman' 
    #   Records must match on Lab, Matrix
    # (🛑 ERROR 🛑)
    print("# END CHECK - Record in ramansettings requires a corresponding record in InstrumentInfo where InstrumentType = 'Raman'")






    print("# CHECK - If InstrumentType = 'FTIR' (in instrumentinfo table) then there must be a corresponding record in the ftirsettings table")
    # CHECK - If InstrumentType = 'FTIR' (in instrumentinfo table) then there must be a corresponding record in the ftirsettings table 
    #   Records must match on Lab, Matrix
    # (🛑 ERROR 🛑)
    
    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_instrumentinfo",
        "badrows": mismatch(
            instrumentinfo[instrumentinfo.instrumenttype == 'FTIR'], 
            ftir, 
            mergecols = [x.lower() for x in instinfomatchcols]
        ), 
        "badcolumn": ','.join(instinfomatchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in Instrumentinfo (where instrumenttype = FTIR) must have a matching record in FTIRSettings. Records are matched on {', '.join(instinfomatchcols)}"
    })
    errs = [*errs, checkData(**args)]
    
    # END OF CHECK - If InstrumentType = 'FTIR' (in instrumentinfo table) then there must be a corresponding record in the ftirsettings table 
    #   Records must match on Lab, Matrix
    # (🛑 ERROR 🛑)
    print("# END OF CHECK - If InstrumentType = 'FTIR' (in instrumentinfo table) then there must be a corresponding record in the ftirsettings table")



    print("# CHECK - Record in ftirsettings requires a corresponding record in InstrumentInfo where InstrumentType = 'FTIR'")
    # CHECK - Record in ftirsettings requires a corresponding record in InstrumentInfo where InstrumentType = 'FTIR' 
    #   Records must match on Lab, Matrix
    # (🛑 ERROR 🛑)

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_ftirsettings",
        "badrows": mismatch(
            ftir, 
            INSTRUMENTINFO_COMBINED[INSTRUMENTINFO_COMBINED.instrumenttype == 'FTIR'], 
            mergecols = [x.lower() for x in instinfomatchcols]
        ), 
        "badcolumn": ','.join(instinfomatchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in FTIRSettings must have a matching record in Instrumentinfo (where instrumenttype = FTIR). Records are matched on {', '.join(instinfomatchcols)}"
    })
    errs = [*errs, checkData(**args)]
    
    # END CHECK - Record in ftirsettings requires a corresponding record in InstrumentInfo where InstrumentType = 'FTIR' 
    #   Records must match on Lab, Matrix
    # (🛑 ERROR 🛑)
    print("# END CHECK - Record in ftirsettings requires a corresponding record in InstrumentInfo where InstrumentType = 'FTIR'")
    








    print("# CHECK - If InstrumentType = 'stereoscope' (in instrumentinfo table) then there must be a corresponding record in the microscopysettings table") 
    # CHECK - If InstrumentType = 'stereoscope' (in instrumentinfo table) then there must be a corresponding record in the microscopysettings table 
    #   Records must match on Lab, Matrix
    # (🛑 ERROR 🛑)

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_instrumentinfo",
        "badrows": mismatch(
            instrumentinfo[instrumentinfo.instrumenttype == 'Stereoscope'], 
            microscopy, 
            mergecols = [x.lower() for x in instinfomatchcols]
        ), 
        "badcolumn": ','.join(instinfomatchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in Instrumentinfo (where instrumenttype = Stereoscope) must have a matching record in MicroscopySettings. Records are matched on {', '.join(instinfomatchcols)}"
    })
    errs = [*errs, checkData(**args)]
    
    # END OF CHECK - If InstrumentType = 'stereoscope' (in instrumentinfo table) then there must be a corresponding record in the microscopysettings table 
    #   Records must match on Lab, Matrix
    # (🛑 ERROR 🛑)
    print("# END OF CHECK - If InstrumentType = 'stereoscope' (in instrumentinfo table) then there must be a corresponding record in the microscopysettings table")
    



    print("# CHECK - Record in microscopysettings requires a corresponding record in InstrumentInfo where InstrumentType = 'stereoscope'")
    # CHECK - Record in microscopysettings requires a corresponding record in InstrumentInfo where InstrumentType = 'stereoscope' 
    #   Records must match on Lab, Matrix
    # (🛑 ERROR 🛑)

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_microscopysettings",
        "badrows": mismatch(
            microscopy, 
            INSTRUMENTINFO_COMBINED[INSTRUMENTINFO_COMBINED.instrumenttype == 'Stereoscope'], 
            mergecols = [x.lower() for x in instinfomatchcols]
        ), 
        "badcolumn": ','.join(instinfomatchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in MicroscopySettings must have a matching record in Instrumentinfo (where instrumenttype = Stereoscope). Records are matched on {', '.join(instinfomatchcols)}"
    })
    errs = [*errs, checkData(**args)]

    # END CHECK - Record in microscopysettings requires a corresponding record in InstrumentInfo where InstrumentType = 'stereoscope' 
    #   Records must match on Lab, Matrix
    # (🛑 ERROR 🛑)
    print("# END CHECK - Record in microscopysettings requires a corresponding record in InstrumentInfo where InstrumentType = 'stereoscope'")
    


    # ------- END InstrumentInfo <-----> Settings tables ------- #






    # --------- InstrumentInfo <-----> SampleReceiving --------- #


    print("""# CHECK - InstrumentInfo Record must match SampleReceiving on Lab and Matrix (two ways)""")
    # CHECK - InstrumentInfo Record must match SampleReceiving on Lab and Matrix (two ways) (🛑 ERROR 🛑)

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_instrumentinfo",
        "badrows": mismatch(
            instrumentinfo, 
            samplereceiving, 
            mergecols = [x.lower() for x in instinfomatchcols]
        ), 
        "badcolumn": ','.join(instinfomatchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in InstrumentInfo must have a matching record in SampleReceiving. Records are matched on {', '.join(instinfomatchcols)}"
    })
    errs = [*errs, checkData(**args)]

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    # NOTE:
    # No problem if an existing record already in database, so we use INSTRUMENTINFO_COMBINED

    args.update({
        "tablename": "tbl_mp_samplereceiving",
        "badrows": mismatch(
            samplereceiving, 
            INSTRUMENTINFO_COMBINED, 
            mergecols = [x.lower() for x in instinfomatchcols]
        ), 
        "badcolumn": ','.join(instinfomatchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in SampleReceiving must have a matching record in Instrumentinfo. Records are matched on {', '.join(instinfomatchcols)}"
    })
    errs = [*errs, checkData(**args)]

    # END CHECK - InstrumentInfo Record must match SampleReceiving on Lab and Matrix (two ways) (🛑 ERROR 🛑)
    print("""# END CHECK - InstrumentInfo Record must match SampleReceiving on Lab and Matrix (two ways)""")


    # ------- END InstrumentInfo <-----> SampleReceiving ------- #
    




    

    # --------- InstrumentInfo <-----> SampleExtraction --------- #
    
    print("""# CHECK - InstrumentInfo Record must match SampleExtraction on Lab and Matrix (two ways)""")
    # CHECK - InstrumentInfo Record must match SampleExtraction on Lab and Matrix (two ways) (🛑 ERROR 🛑)

    
    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_instrumentinfo",
        "badrows": mismatch(
            instrumentinfo, 
            sampleextraction, 
            mergecols = [x.lower() for x in instinfomatchcols]
        ), 
        "badcolumn": ','.join(instinfomatchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in InstrumentInfo must have a matching record in sampleextraction. Records are matched on {', '.join(instinfomatchcols)}"
    })
    errs = [*errs, checkData(**args)]

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    # NOTE:
    # No problem if an existing record already in database, so we use INSTRUMENTINFO_COMBINED
    args.update({
        "tablename": "tbl_mp_sampleextraction",
        "badrows": mismatch(
            sampleextraction, 
            INSTRUMENTINFO_COMBINED, 
            mergecols = [x.lower() for x in instinfomatchcols]
        ), 
        "badcolumn": ','.join(instinfomatchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in sampleextraction must have a matching record in Instrumentinfo. Records are matched on {', '.join(instinfomatchcols)}"
    })
    errs = [*errs, checkData(**args)]
    # END CHECK - InstrumentInfo Record must match SampleExtraction on Lab and Matrix (two ways) (🛑 ERROR 🛑)
    print("""# END CHECK - InstrumentInfo Record must match SampleExtraction on Lab and Matrix (two ways)""")
    
    # ------- END InstrumentInfo <-----> SampleExtraction ------- #


    # ----------------------------- END Relating InstrumentInfo tab to the other tables ------------------------- #






    # ---------------------------- Relating Sample Extraction to Sample Receiving ------------------------------- #

    print("""# SampleExtraction must match SampleReceiving on StationID, SampleDate, Lab, Matrix, SampleType, FieldReplicate (and Vice Versa)""")
    # SampleExtraction must match SampleReceiving on StationID, SampleDate, Lab, Matrix, SampleType, FieldReplicate (and Vice Versa) (🛑 ERROR 🛑)

    samplematchcols = ['StationID', 'SampleDate', 'Lab', 'Matrix', 'SampleType', 'FieldReplicate' ]

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_samplereceiving",
        "badrows": mismatch(
            samplereceiving, 
            sampleextraction, 
            mergecols = [x.lower() for x in samplematchcols]
        ), 
        "badcolumn": ','.join(samplematchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in SampleReceiving must have a matching record in SampleExtraction. Records are matched on {', '.join(samplematchcols)}"
    })
    errs = [*errs, checkData(**args)]

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    args.update({
        "tablename": "tbl_mp_sampleextraction",
        "badrows": mismatch(
            sampleextraction, 
            samplereceiving, 
            mergecols = [x.lower() for x in samplematchcols]
        ), 
        "badcolumn": ','.join(samplematchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in SampleExtraction must have a matching record in SampleReceiving. Records are matched on {', '.join(samplematchcols)}"
    })
    errs = [*errs, checkData(**args)]


    # END SampleExtraction must match SampleReceiving on StationID, SampleDate, Lab, Matrix, SampleType, FieldReplicate (and Vice Versa) (🛑 ERROR 🛑)
    print("""# END SampleExtraction must match SampleReceiving on StationID, SampleDate, Lab, Matrix, SampleType, FieldReplicate (and Vice Versa)""")
    
    # -------------------------- END Relating Sample Extraction to Sample Receiving ----------------------------- #


    # ---------------------------- Relating Sample Extraction to Microscopy settings ------------------------------- #

    print("""# SampleExtraction must match MicroscopySettings on 'stationid','sampledate','lab','matrix','sampletype','fieldreplicate','sampleid','labbatch','sizefraction' (and Vice Versa)""")
    # SampleExtraction must match MicroscopySettings on 'stationid','sampledate','lab','matrix','sampletype','fieldreplicate','sampleid','labbatch','sizefraction' (and Vice Versa) (🛑 ERROR 🛑)

    sampleextract_microscopy_matchcols = ['stationid','sampledate','lab','matrix','sampletype','fieldreplicate','sampleid','labbatch','sizefraction' ]

    # Created Coder: Robert Butler
    # Created Date: 2/13/2024
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_microscopysettings",
        "badrows": mismatch(
            microscopysettings, 
            sampleextraction, 
            mergecols = [x.lower() for x in sampleextract_microscopy_matchcols]
        ), 
        "badcolumn": ','.join(sampleextract_microscopy_matchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in MicroscopySettings must have a matching record in SampleExtraction. Records are matched on {', '.join(sampleextract_microscopy_matchcols)}"
    })
    errs = [*errs, checkData(**args)]

    # Created Coder: Robert Butler
    # Created Date: 2/13/2024
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    args.update({
        "tablename": "tbl_mp_sampleextraction",
        "badrows": mismatch(
            sampleextraction, 
            microscopysettings, 
            mergecols = [x.lower() for x in sampleextract_microscopy_matchcols]
        ), 
        "badcolumn": ','.join(sampleextract_microscopy_matchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in SampleExtraction must have a matching record in MicroscopySettings. Records are matched on {', '.join(sampleextract_microscopy_matchcols)}"
    })
    errs = [*errs, checkData(**args)]


    # END SampleExtraction must match MicroscopySettings on 'stationid','sampledate','lab','matrix','sampletype','fieldreplicate','sampleid','labbatch','sizefraction' (and Vice Versa) (🛑 ERROR 🛑)
    print("""# END SampleExtraction must match MicroscopySettings on 'stationid','sampledate','lab','matrix','sampletype','fieldreplicate','sampleid','labbatch','sizefraction' (and Vice Versa)""")
    
    # -------------------------- END Relating Sample Extraction to Microscopy settings ----------------------------- #




    ############################################################################################################################################




    # ------------------------------- BEGIN Relating LabInfo tab to the other tables --------------------------- #

    # ------- LabInfo <-----> Sample Receiving ------- #

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_samplereceiving",
        "badrows": mismatch(
            samplereceiving, 
            labinfo, 
            left_mergecols = ['stationid','sampledate','lab','matrix','datereceived'],
            right_mergecols = ['stationid','sampledate','lab','matrix','startdate']
        ), 
        "badcolumn": ','.join(['stationid','sampledate','lab','matrix','datereceived']),
        "error_type": "Logic Error",
        "error_message": f"Each record in SampleReceiving must have a matching record in labinfo. Records are matched on StationID, SampleDate, Lab, Matrix, StartDate/DateReceived"
    })
    errs = [*errs, checkData(**args)]

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    args.update({
        "tablename": "tbl_mp_labinfo",
        "badrows": mismatch(
            labinfo, 
            samplereceiving, 
            left_mergecols = ['stationid','sampledate','lab','matrix','startdate'],
            right_mergecols = ['stationid','sampledate','lab','matrix','datereceived']
        ), 
        "badcolumn": ','.join(['stationid','sampledate','lab','matrix','startdate']),
        "error_type": "Logic Error",
        "error_message": f"Each record in labinfo must have a matching record in SampleReceiving. Records are matched on StationID, SampleDate, Lab, Matrix, DateReceived/StartDate"
    })
    errs = [*errs, checkData(**args)]

    # ------- END LabInfo <-----> Sample Receiving ------- #
    





    # ------- LabInfo <-----> Sample Extraction ------- #

    labsamplematchcols = ['StationID', 'SampleDate', 'Lab', 'Matrix', 'LabBatch', 'FieldReplicate']
    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_labinfo",
        "badrows": mismatch(
            labinfo, 
            sampleextraction, 
            mergecols = [x.lower() for x in labsamplematchcols]
        ), 
        "badcolumn": ','.join(labsamplematchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in labinfo must have a matching record in SampleExtraction. Records are matched on {', '.join(labsamplematchcols)}"
    })
    errs = [*errs, checkData(**args)]

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    args.update({
        "tablename": "tbl_mp_sampleextraction",
        "badrows": mismatch(
            sampleextraction,
            labinfo,
            mergecols = [x.lower() for x in labsamplematchcols]
        ),
        "badcolumn": ','.join(labsamplematchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in SampleExtraction must have a matching record in labinfo. Records are matched on {', '.join(labsamplematchcols)}"
    })
    errs = [*errs, checkData(**args)]
    # ------- END LabInfo <-----> Sample Extraction ------- #
    

    # ------- LabInfo <-----> InstrumentInfo ------- #

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_instrumentinfo",
        "badrows": mismatch(
            instrumentinfo, 
            labinfo, 
            mergecols = [x.lower() for x in instinfomatchcols]
        ), 
        "badcolumn": ','.join(instinfomatchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in InstrumentInfo must have a matching record in labinfo. Records are matched on {', '.join(instinfomatchcols)}"
    })
    errs = [*errs, checkData(**args)]

    # Created Coder: Robert Butler
    # Created Date: 08/25/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    args.update({
        "tablename": "tbl_mp_labinfo",
        "badrows": mismatch(
            labinfo, 
            # No problem if an existing record already in database, so we use INSTRUMENTINFO_COMBINED
            INSTRUMENTINFO_COMBINED, 
            mergecols = [x.lower() for x in instinfomatchcols]
        ), 
        "badcolumn": ','.join(instinfomatchcols),
        "error_type": "Logic Error",
        "error_message": f"Each record in labinfo must have a matching record in Instrumentinfo. Records are matched on {', '.join(instinfomatchcols)}"
    })
    errs = [*errs, checkData(**args)]

    # ------- END LabInfo <-----> InstrumentInfo ------- #


    # -------------------------------- END Relating LabInfo tab to the other tables ---------------------------- #



    # ---------------------------------------------------------------------------------------------------- #
    # -------------- END OF Traditional Logic Checks - Checking relationships between tables ------------- #
    # ---------------------------------------------------------------------------------------------------- #
    
    

    ######################################################################################################################
    # ------------------------------------------------------------------------------------------------------------------ #
    # --------------------------------------------- END OF Logic Checks ------------------------------------------------ #
    # ------------------------------------------------------------------------------------------------------------------ #
    ######################################################################################################################




    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #





    ###############################################################################################################################
    # --------------------------------------------------------------------------------------------------------------------------- #
    # -------------------------------------------------- Results Tab Checks ----------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------------------- #
    ###############################################################################################################################






    print("""# CHECK - If the matrix is sediment, then the stationid must come from lu_station (stationid column)""")
    # Description: If the matrix is sediment, then the stationid must come from lu_station (stationid column) (🛑 ERROR 🛑)
    # Created Coder: Nick Lombardo
    # Created Date: 08/28/23
    # Last Edited Date: 09/01/2023
    # Last Edited Coder: Robert Butler
    # NOTE (MM/DD/YY): Added a link to the stations lookup list

    lu_station = pd.read_sql('SELECT DISTINCT stationid FROM lu_station', g.eng).stationid
    errs = [
        *errs,
        checkData(
            tablename = 'tbl_mp_results',
            # matrix column is from lu_matrix, so this case should always match
            badrows = results[(results['matrix'] == 'Sediment') & (~results['stationid'].isin(lu_station))].tmp_row.tolist(),
            badcolumn = "StationID",
            error_type = "Value Error",
            error_message = "If the matrix is sediment, then the StationID must come from the <a target=_blank href=scraper?action=help&layer=lu_station>Bight 2023 Stations Lookup List</a>"
        )
    ]



    # END OF CHECK - If the matrix is sediment, then the stationid must come from lu_station (stationid column) (🛑 ERROR 🛑)
    print("""# END OF CHECK - If the matrix is sediment, then the stationid must come from lu_station (stationid column)""")


    print("""# CHECK - Moisture content should be an number from 0 to 100""")
    # Description: Moisture content should be an number from 0 to 100 (🛑 ERROR 🛑)
    # Created Coder: Nick Lombardo
    # Created Date: 08/28/23
    # Last Edited Date: 8/31/2023
    # Last Edited Coder: Robert Butler
    # NOTE (08/31/2023): Moisturecontent doesnt need to be an integer necessarily - confirmed by Leah on 8/31/2023

    moisture_content_outside_0_to_100 = (results['moisturecontent'] < 0) | (results['moisturecontent'] > 100)

    errs = [
        *errs,
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[moisture_content_outside_0_to_100].tmp_row.tolist(),
            badcolumn = "MoistureContent",
            error_type = "Value Error",
            error_message = "Moisture content must be an number between 0 and 100"
        )
    ]


    # END OF CHECK - Moisture content should be an number from 0 to 100 (🛑 ERROR 🛑)
    print("""# END OF CHECK - Moisture content should be an number from 0 to 100""")
 
 
    print("""# CHECK - MoistureContent required if matrix is 'Sediment'""")
    # Description: MoistureContent required if matrix is 'Sediment' (🛑 ERROR 🛑)
    # Created Coder: Robert Butler
    # Created Date: 8/31/2023
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    errs = [
        *errs,
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[(results.matrix == 'Sediment') & (results.moisturecontent.isnull())].tmp_row.tolist(),
            badcolumn = "MoistureContent",
            error_type = "Value Error",
            error_message = "MoistureContent required if matrix is 'Sediment'"
        )
    ]


    # END OF CHECK - MoistureContent required if matrix is 'Sediment' (🛑 ERROR 🛑)
    print("""# END OF CHECK - MoistureContent required if matrix is 'Sediment'""")




    print("""# CHECK - ParticleID should be unique in the results table. """)
    # Description: ParticleID should be unique in the results table. 
    #     Check for a duplicate particleID in their submission, and check if the same particleID name already exists in the results table in the database 
    # (🛑 ERROR 🛑)
    # Created Coder: Nick Lombardo
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA


    # in submission
    errs = [
        *errs,
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[results.duplicated(subset='particleid', keep=False)].tmp_row.tolist(),
            badcolumn = "ParticleID",
            error_type = "Value Error",
            error_message = "Duplicate ParticleID in submission"
        )
    ]

    # in database
    particle_ids_in_db = pd.read_sql('SELECT DISTINCT particleid from tbl_mp_results', g.eng).particleid
    errs = [
        *errs,
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[results['particleid'].isin(particle_ids_in_db)].tmp_row.tolist(),
            badcolumn = "ParticleID",
            error_type = "Value Error",
            error_message = "This ParticleID already exists in database"
        )
    ]

    # END OF CHECK - ParticleID should be unique in the results table. 
    #     Check for a duplicate particleID in their submission, and check if the same particleID name already exists in the results table in the database 
    # (🛑 ERROR 🛑)
    print("""# END OF CHECK - ParticleID should be unique in the results table. """)



    print("""# CHECK - Length column should be from 0 to 5000um (non inclusive range)""")
    # CHECK - Length column should be from 0 to 5000um (non inclusive range) (🛑 ERROR 🛑)
    
    # Created Coder: Robert Butler
    # Created Date: 08/28/23
    # Last Edited Date: 08/31/23
    # Last Edited Coder: Robert Butler
    # NOTE (08/31/23): made this an error rather than warning - Robert

    errs.append(
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[~results['length_um'].between(0, 5000, inclusive='neither')].tmp_row.tolist(),
            badcolumn = "Length_um",
            error_type = "Value Error",
            error_message = "Length should be a number between 0 and 5000um (non-inclusive)"
        )
    )

    # END OF CHECK - Length column should be from 0 to 5000um (non inclusive range) (🛑 ERROR 🛑)
    print("""# END OF CHECK - Length column should be from 0 to 5000um (non inclusive range)""")


    print("""# CHECK - Width column shuold be from 0 to 5000 um (non inclusive range)""")
    # CHECK - Width column shuold be from 0 to 5000 um (non inclusive range) (🛑 ERROR 🛑)
    
    # Created Coder: Robert Butler
    # Created Date: 08/28/23
    # Last Edited Date: 08/31/23
    # Last Edited Coder: Robert Butler
    # NOTE (08/31/23): Changed error_message to Width instead of Length - Nick
    # NOTE (08/31/23): made this an error rather than warning - Robert

    errs.append(
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[~results['width_um'].between(0, 5000, inclusive='neither')].tmp_row.tolist(),
            badcolumn = "Width_um",
            error_type = "Value Error",
            error_message = "Width should be a number between 0 and 5000um (non-inclusive)"
        )
    )

    # END OF CHECK - Width column shuold be from 0 to 5000 um (non inclusive range) (🛑 ERROR 🛑)
    print("""# END OF CHECK - Width column shuold be from 0 to 5000 um (non inclusive range)""")
  
  
    print("""# CHECK - Length column should not be from 0 to 125um (non inclusive range)""")
    # CHECK - Length column should not be from 0 to 125um (non inclusive range) (🟡 WARNING 🟡)
    
    # Created Coder: Robert Butler
    # Created Date: 08/31/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    warnings.append(
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[results['length_um'].between(0, 125, inclusive='neither')].tmp_row.tolist(),
            badcolumn = "Length_um",
            error_type = "Value Error",
            error_message = "Length should be 125um or above"
        )
    )

    # END OF CHECK - Length column should not be from 0 to 125um (non inclusive range) (🟡 WARNING 🟡)
    print("""# END OF CHECK - Length column should not be from 0 to 125um (non inclusive range)""")


    print("""# CHECK - Width column should not be from 0 to 125 um (non inclusive range)""")
    # CHECK - Width column should not be from 0 to 125 um (non inclusive range) (🟡 WARNING 🟡)
    
    # Created Coder: Robert Butler
    # Created Date: 08/31/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    warnings.append(
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[results['width_um'].between(0, 125, inclusive='neither')].tmp_row.tolist(),
            badcolumn = "Width_um",
            error_type = "Value Error",
            error_message = "Width should be 125um or above"
        )
    )

    # END OF CHECK - Width column should not be from 0 to 125 um (non inclusive range) (🟡 WARNING 🟡)
    print("""# END OF CHECK - Width column should not be from 0 to 125 um (non inclusive range)""")


    print("""# CHECK - If Raman = 'Yes' Then raman_chemicalid cannot be 'not measured' nor can it be left blank """)
    # CHECK - If Raman = 'Yes' Then raman_chemicalid cannot be 'not measured' nor can it be left blank  (🛑 ERROR 🛑)

    # Created Coder: Robert Butler
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    errs.append(
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[ 
                (results['raman'] == 'Yes') 
                & (
                    (results['raman_chemicalid'].fillna('').astype(str).str.lower() == 'not measured') |
                    (results['raman_chemicalid'].fillna('').astype(str).str.replace("\s*","", regex = True) == '') 
                )
            ].tmp_row.tolist(),
            badcolumn = "raman_chemicalid",
            error_type = "Value Error",
            error_message = "If the Raman column says 'Yes' then the raman_chemicalid cannot say 'not measured' nor can it be left blank."
        )
    )

    # END OF CHECK - If Raman = 'Yes' Then raman_chemicalid cannot be 'not measured' nor can it be left blank (🛑 ERROR 🛑)
    print("""# END OF CHECK - If Raman = 'Yes' Then raman_chemicalid cannot be 'not measured' nor can it be left blank""")


    print("""# CHECK - If FTIR = 'Yes' (in results table) then ftir_chemicalid cannot be 'not measured' nor can it be left blank""")
    # CHECK - If FTIR = 'Yes' (in results table) then ftir_chemicalid cannot be 'not measured' nor can it be left blank (🛑 ERROR 🛑)
    
    # Created Coder: Robert Butler
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    errs.append(
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[ 
                (results['ftir'] == 'Yes') 
                & (
                    (results['ftir_chemicalid'].fillna('').astype(str).str.lower() == 'not measured') |
                    (results['ftir_chemicalid'].fillna('').astype(str).str.replace("\s*","", regex = True) == '') 
                )
            ].tmp_row.tolist(),
            badcolumn = "ftir_chemicalid",
            error_type = "Value Error",
            error_message = "If the FTIR column says 'Yes' then the ftir_chemicalid cannot say 'not measured' nor can it be left blank."
        )
    )
    
    # END OF CHECK - If FTIR = 'Yes' (in results table) then ftir_chemicalid cannot be 'not measured' nor can it be left blank (🛑 ERROR 🛑)
    print("""# END OF CHECK - If FTIR = 'Yes' (in results table) then ftir_chemicalid cannot be 'not measured' nor can it be left blank""")


    print("""# CHECK - If the 'Raman' or 'FTIR' column says 'Yes' then the PolymerID cannot be 'Not measured'""")
    # CHECK - If the 'Raman' or 'FTIR' column says 'Yes' then the PolymerID cannot be 'Not measured' (🛑 ERROR 🛑)

    # Created Coder: Robert Butler
    # Created Date: 08/31/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    errs.append(
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[ ((results.raman == 'Yes') | (results.ftir == 'Yes')) & (results.polymerid == 'Not measured') ].tmp_row.tolist(),
            badcolumn = "polymerid",
            error_type = "Value Error",
            error_message = "If the 'Raman' or 'FTIR' column says 'Yes' then the PolymerID cannot be 'Not measured'"
        )
    )

    # END OF CHECK - If the 'Raman' or 'FTIR' column says 'Yes' then the PolymerID cannot be 'Not measured' (🛑 ERROR 🛑)
    print("""# END OF CHECK - If the 'Raman' or 'FTIR' column says 'Yes' then the PolymerID cannot be 'Not measured'""")



    print("""# CHECK - If SampleType is Lab blank, then the StationID must be '0000'""")
    # CHECK - If SampleType is Lab blank, then the StationID must be '0000' (🛑 ERROR 🛑)

    # Created Coder: Robert Butler
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    errs.append(
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[ (results.sampletype == 'Lab blank') & (results.stationid.astype(str) != '0000')].tmp_row.tolist(),
            badcolumn = "stationid,sampletype",
            error_type = "Value Error",
            error_message = "If SampleType is Lab blank, then the StationID must be '0000'"
        )
    )

    # END OF CHECK - If SampleType is Lab blank, then the StationID must be '0000' (🛑 ERROR 🛑)
    print("""# END OF CHECK - If SampleType is Lab blank, then the StationID must be '0000'""")


    print("""# CHECK - If SampleType is Result or Field blank, then the StationID must not be '0000'""")
    # CHECK - If SampleType is Result or Field blank, then the StationID must not be '0000' (🛑 ERROR 🛑)
    
    # Created Coder: Robert Butler
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    errs.append(
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[ (results.sampletype.isin(['Field blank', 'Result'])) & (results.stationid == '0000')].tmp_row.tolist(),
            badcolumn = "stationid,sampletype",
            error_type = "Value Error",
            error_message = "If SampleType is Field blank or Result, then the StationID must not be '0000'"
        )
    )
    
    # END OF CHECK - If SampleType is Result or Field blank, then the StationID must not be '0000' (🛑 ERROR 🛑)
    print("""# END OF CHECK - If SampleType is Result or Field blank, then the StationID must not be '0000'""")


    print("""# CHECK - TimeImagesMeasurements must be in hours - warn if over __ saying that they should not report in minutes """)
    # CHECK - TimeImagesMeasurements must be in hours - warn if over __ saying that they should not report in minutes (🟡 WARNING 🟡)
    
    # Created Coder: Robert Butler
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    warnings.append(
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[results.timeimagesmeasurements_hours > 15].tmp_row.tolist(),
            badcolumn = "timeimagesmeasurements_hours",
            error_type = "Value Error",
            error_message = "TimeImagesMeasurements_Hours must be reported in hours. This value seems unusually high, so it may have been recorded in minutes."
        )
    )
    
    # END OF CHECK - TimeImagesMeasurements must be in hours - warn if over __ saying that they should not report in minutes (🟡 WARNING 🟡)
    print("""# END OF CHECK - TimeImagesMeasurements must be in hours - warn if over __ saying that they should not report in minutes """)


    print("""# CHECK - If TimeImagesMeasurements is less than 0, it must be -88 """)
    # CHECK - If TimeImagesMeasurements is less than 0, it must be -88 (🛑 ERROR 🛑)

    # Created Coder: Robert Butler
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    errs.append(
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[(results.timeimagesmeasurements_hours < 0) & (results.timeimagesmeasurements_hours != -88) ].tmp_row.tolist(),
            badcolumn = "timeimagesmeasurements_hours",
            error_type = "Value Error",
            error_message = "TimeImagesMeasurements should not be a negative number, unless it is -88 to indicate a missing value"
        )
    )

    # END OF CHECK - If TimeImagesMeasurements is less than 0, it must be -88 (🛑 ERROR 🛑)
    print("""# END OF CHECK - If TimeImagesMeasurements is less than 0, it must be -88 """)


    print("""# CHECK - If "Other_instrument_used" = 'Yes' then "Other_InstrumentType" must not be left blank, nor should it say 'not recorded' """)
    # CHECK - If "Other_instrument_used" = 'Yes' then "Other_InstrumentType" must not be left blank, nor should it say 'not recorded' (🛑 ERROR 🛑)

    # Created Coder: Robert Butler
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    errs.append(
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[
                (results.other_instrument_used == 'Yes') 
                & (
                    (results['other_instrumenttype'].fillna('').astype(str).str.lower() == 'not recorded') |
                    (results['other_instrumenttype'] == '') |
                    (results['other_instrumenttype'].isna()) |
                    (results['other_instrumenttype'].fillna('').astype(str).str.replace("\s*","", regex = True) == '') 
                )
            ].tmp_row.tolist(),
            badcolumn = "other_instrumenttype",
            error_type = "Value Error",
            error_message = " If 'Other_instrument_used' = 'Yes' then 'Other_InstrumentType' must not be left blank, nor should it say 'not recorded'"
        )
    )

    # END OF CHECK - If "Other_instrument_used" = 'Yes' then "Other_InstrumentType" must not be left blank, nor should it say 'not recorded' (🛑 ERROR 🛑)
    print("""# END OF CHECK - If "Other_instrument_used" = 'Yes' then "Other_InstrumentType" must not be left blank, nor should it say 'not recorded' """)


    print("""# CHECK - If "Other_instrument_used" = 'Yes' then "Other_chemicalid" must not be left blank, nor should it say 'not measured' """)
    # CHECK - If "Other_instrument_used" = 'Yes' then "Other_chemicalid" must not be left blank, nor should it say 'not measured' (🛑 ERROR 🛑)

    # Created Coder: Robert Butler
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    errs.append(
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[
                (results.other_instrument_used == 'Yes') 
                & (
                    (results['other_chemicalid'].fillna('').astype(str).str.lower() == 'not measured') |
                    (results['other_chemicalid'] == '') |
                    (results['other_chemicalid'].isna()) |
                    (results['other_chemicalid'].fillna('').astype(str).str.replace("\s*","", regex = True) == '') 
                )
            ].tmp_row.tolist(),
            badcolumn = "other_chemicalid",
            error_type = "Value Error",
            error_message = " If 'Other_instrument_used' = 'Yes' then 'Other_chemicalid' must not be left blank, nor should it say 'not measured'"
        )
    )

    # END OF CHECK - If "Other_instrument_used" = 'Yes' then "Other_chemicalid" must not be left blank, nor should it say 'not measured' (🛑 ERROR 🛑)
    print("""# END OF CHECK - If "Other_instrument_used" = 'Yes' then "Other_chemicalid" must not be left blank, nor should it say 'not measured' """)



    print("""# CHECK - If "Other_instrument_used" = 'No' then Other_InstrumentType must be left blank """)
    # CHECK - If "Other_instrument_used" = 'No' then Other_InstrumentType must be left blank (🛑 ERROR 🛑)
    
    # Created Coder: Robert Butler
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    errs.append(
        checkData(
            tablename = 'tbl_mp_results',
            badrows = results[
                (results.other_instrument_used == 'No') 
                & ~(
                    (results['other_instrumenttype'] == '') |
                    (results['other_instrumenttype'].isna()) 
                )
            ].tmp_row.tolist(),
            badcolumn = "other_instrumenttype",
            error_type = "Value Error",
            error_message = " If 'Other_instrument_used' = 'No' then 'Other_InstrumentType' must be left blank"
        )
    )
    
    # END OF CHECK - If "Other_instrument_used" = 'No' then Other_InstrumentType must be left blank (🛑 ERROR 🛑)
    print("""# END OF CHECK - If "Other_instrument_used" = 'No' then Other_InstrumentType must be left blank """)






    ###############################################################################################################################
    # --------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------ END OF Results Tab Checks ------------------------------------------------ #
    # --------------------------------------------------------------------------------------------------------------------------- #
    ###############################################################################################################################






    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #








    ######################################################################################################################################
    # ---------------------------------------------------------------------------------------------------------------------------------- #
    # -------------------------------------------------- InstrumentInfo Tab Checks ----------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------------------------- #
    ######################################################################################################################################




    print("""# CHECK - If instrumenttype = 'Other' then a comment is required""")
    # CHECK - If instrumenttype = 'Other' then a comment is required (🛑 ERROR 🛑)

    # Created Coder: Robert Butler
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    errs.append(
        checkData(
            tablename = 'tbl_mp_instrumentinfo',
            badrows = instrumentinfo[
                (instrumentinfo.instrumenttype == 'Other') 
                & (instrumentinfo['comments'].fillna('').astype(str).str.replace("\s*","", regex = True) == '')
            ].tmp_row.tolist(),
            badcolumn = "comments",
            error_type = "Value Error",
            error_message = " If 'instrumenttype' = 'Other' then a comment is required"
        )
    )

    # END OF CHECK - If instrumenttype = 'Other' then a comment is required (🛑 ERROR 🛑)
    print("""# END OF CHECK - If instrumenttype = 'Other' then a comment is required""")



    print("""# CHECK - Required Columns - 'SoftwareCollection', 'SoftwareProcessing', 'SoftwareMatching', 'SpectralLibraries', 'LibraryDetails', 'CalibrationFrequency' """)
    # CHECK - Required Columns - 'SoftwareCollection', 'SoftwareProcessing', 'SoftwareMatching', 'SpectralLibraries', 'LibraryDetails', 'CalibrationFrequency' 
    #       ***Unless the instrumenttype is "Other" or "Stereoscope"
    # (🛑 ERROR 🛑)

    # Created Coder: Robert Butler
    # Created Date: 08/28/23
    # Last Edited Date: 08/31/23
    # Last Edited Coder: Nick Lombardo
    # NOTE (08/31/23): Fixed badcolumn reference to col in requiredcols, fixed badrows definition
    #                   from (instrumentinfo.instrumenttype.isin(['Other','Stereoscope'])) to
    #                   (~instrumentinfo.instrumenttype.isin(['Other','Stereoscope'])) 

    requiredcols = ['softwarecollection', 'softwareprocessing', 'softwarematching', 'spectrallibraries', 'librarydetails', 'calibrationfrequency']
    for col in requiredcols:
        errs.append(
            checkData(
                tablename = 'tbl_mp_instrumentinfo',
                badrows = instrumentinfo[
                    (~instrumentinfo.instrumenttype.isin(['Other','Stereoscope'])) 
                    & (
                        (instrumentinfo[col] == '') |
                        (instrumentinfo[col].isna()) 
                    )
                ].tmp_row.tolist(),
                badcolumn = col,
                error_type = "Value Error",
                error_message = f"The column {col} is required to be filled in, unless the instrument type is 'Other' or 'Stereoscope'"
            )
        )


    # END OF CHECK - Required Columns - 'SoftwareCollection', 'SoftwareProcessing', 'SoftwareMatching', 'SpectralLibraries', 'LibraryDetails', 'CalibrationFrequency' 
    #       ***Unless the instrumenttype is "Other" or "Stereoscope"
    # (🛑 ERROR 🛑)
    print("""# END OF CHECK - Required Columns - 'SoftwareCollection', 'SoftwareProcessing', 'SoftwareMatching', 'SpectralLibraries', 'LibraryDetails', 'CalibrationFrequency' """)



    ######################################################################################################################################
    # ---------------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------ END OF InstrumentInfo Tab Checks ------------------------------------------------ #
    # ---------------------------------------------------------------------------------------------------------------------------------- #
    ######################################################################################################################################





    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #





    ######################################################################################################################################
    # ---------------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------------ LabInfo Tab Checks -------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------------------------- #
    ######################################################################################################################################





    print("""# CHECK - If [AirFiltration/ClothingPolicy/SealedEnvironment] is "Yes" then [AirFiltration/ClothingPolicy/SealedEnvironment]Type must not be empty """)
    # CHECK - If [AirFiltration/ClothingPolicy/SealedEnvironment] is "Yes" then [AirFiltration/ClothingPolicy/SealedEnvironment]Type must not be empty (🛑 ERROR 🛑)
    
    print("""# ALSO CHECK - If [AirFiltration/ClothingPolicy/SealedEnvironment] is "No" then [AirFiltration/ClothingPolicy/SealedEnvironment]Type must be empty """)
    # ALSO CHECK - If [AirFiltration/ClothingPolicy/SealedEnvironment] is "No" then [AirFiltration/ClothingPolicy/SealedEnvironment]Type must be empty (🛑 ERROR 🛑)
    
    cols = ['airfiltration','sealedenvironment','clothingpolicy']
    for col in cols:
        # If Yes, then the "type" col cant be blank
        errs.append(
            checkData(
                tablename = 'tbl_mp_labinfo',
                badrows = labinfo[
                    (labinfo[col] == 'Yes' ) 
                    & (
                        (labinfo[f"{col}type"] == '') |
                        (labinfo[f"{col}type"].isna()) 
                    )
                ].tmp_row.tolist(),
                badcolumn = f"{col}type",
                error_type = "Value Error",
                error_message = f"If the column {col} is 'Yes' then {col}type must not be empty"
            )
        )
        
        # If No, then the "type" col must be blank
        errs.append(
            checkData(
                tablename = 'tbl_mp_labinfo',
                badrows = labinfo[
                    (labinfo[col] == 'No' ) 
                    & ~(
                        (labinfo[f"{col}type"] == '') |
                        (labinfo[f"{col}type"].isna()) 
                    )
                ].tmp_row.tolist(),
                badcolumn = f"{col}type",
                error_type = "Value Error",
                error_message = f"If the column {col} is 'No' then {col}type must be empty"
            )
        )

    # END OF CHECK - If [AirFiltration/ClothingPolicy/SealedEnvironment] is "Yes" then [AirFiltration/ClothingPolicy/SealedEnvironment]Type must not be empty (🛑 ERROR 🛑)
    # ALSO END OF CHECK - If [AirFiltration/ClothingPolicy/SealedEnvironment] is "No" then [AirFiltration/ClothingPolicy/SealedEnvironment]Type must be empty (🛑 ERROR 🛑)
    print("""# END OF CHECK - If [AirFiltration/ClothingPolicy/SealedEnvironment] is "Yes" then [AirFiltration/ClothingPolicy/SealedEnvironment]Type must not be empty """)
    print("""# ALSO END OF CHECK - If [AirFiltration/ClothingPolicy/SealedEnvironment] is "No" then [AirFiltration/ClothingPolicy/SealedEnvironment]Type must be empty """)

    
    print("""# CHECK - StartDate must not be before July 2023, nor after the date of their submission (today()) """)
    # CHECK - StartDate must not be before July 2023, nor after the date of their submission (today()) (🛑 ERROR 🛑)

    # Created Coder: Robert Butler (using ChatGPT) (https://chat.openai.com/share/0156665e-b8de-449a-9739-f89c0ae1f8b1)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    # Define the earliest allowed StartDate and the current date
    start_date_boundary = pd.Timestamp('2023-07-01')
    current_date = pd.Timestamp(datetime.now().date())

    # Filter rows where StartDate is before the boundary or after the current date
    invalid_start_dates = labinfo[
        (labinfo['startdate'] < start_date_boundary) | 
        (labinfo['startdate'] > current_date)
    ].tmp_row.tolist()

    errs.append(
        checkData(
            tablename='tbl_mp_labinfo',
            badrows=invalid_start_dates,
            badcolumn='StartDate',
            error_type='Date Error',
            error_message='StartDate must not be before July 2023, nor after the date of their submission.'
        )
    )

    # END OF CHECK - StartDate must not be before July 2023, nor after the date of their submission (today()) (🛑 ERROR 🛑)
    print("""# END OF CHECK - StartDate must not be before July 2023, nor after the date of their submission (today()) """)


    print("""# CHECK - EndDate must not be before StartDate """)
    # CHECK - EndDate must not be before StartDate (🛑 ERROR 🛑)

    # Filter rows where EndDate is before StartDate
    invalid_end_dates = labinfo[
        labinfo['enddate'] < labinfo['startdate']
    ].tmp_row.tolist()

    errs.append(
        checkData(
            tablename='tbl_mp_labinfo',
            badrows=invalid_end_dates,
            badcolumn='StartDate,EndDate',
            error_type='Date Error',
            error_message='EndDate must not be before StartDate.'
        )
    )

    # END OF CHECK - EndDate must not be before StartDate (🛑 ERROR 🛑)
    print("""# END OF CHECK - EndDate must not be before StartDate """)




    ######################################################################################################################################
    # ---------------------------------------------------------------------------------------------------------------------------------- #
    # ---------------------------------------------------- END OF LabInfo Tab Checks --------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------------------------- #
    ######################################################################################################################################








    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #








    ###############################################################################################################################################
    # ------------------------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------------ SampleExtraction Tab Checks -------------------------------------------------------- #
    # ------------------------------------------------------------------------------------------------------------------------------------------- #
    ###############################################################################################################################################


    print("""# CHECK - Range for FilterDiameter is 0 to 100 """)
    # CHECK - Range for FilterDiameter is 0 to 100 (🟡 WARNING 🟡)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: 9/1/2023
    # Last Edited Coder: Robert Butler
    # NOTE (9/1/2023): Made acceptable range non inclusive

    invalid_diameter = sampleextraction[
        (sampleextraction['filterdiameter_mm'] <= 0) | 
        (sampleextraction['filterdiameter_mm'] >= 100)
    ].tmp_row.tolist()

    warnings.append(
        checkData(
            tablename='tbl_mp_sampleextraction',
            badrows=invalid_diameter,
            badcolumn='filterdiameter_mm',
            error_type='Range Warning',
            error_message='filterdiameter_mm should be between 0 and 100.'
        )
    )

    # END OF CHECK - Range for FilterDiameter is 0 to 100 (🟡 WARNING 🟡)
    print("""# END OF CHECK - Range for FilterDiameter is 0 to 100 """)


    print("""# CHECK - Range for FilterDiameter must not be negative """)
    # CHECK - Range for FilterDiameter must not be negative (🛑 ERROR 🛑)
    # Created Coder: Robert Butler 
    # Created Date: 09/1/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    invalid_diameter = sampleextraction[
        (sampleextraction['filterdiameter_mm'] < 0) 
    ].tmp_row.tolist()

    errs.append(
        checkData(
            tablename='tbl_mp_sampleextraction',
            badrows=invalid_diameter,
            badcolumn='filterdiameter_mm',
            error_type='Range Warning',
            error_message='filterdiameter_mm cannot be negative.'
        )
    )

    # END OF CHECK - Range for FilterDiameter must not be negative (🛑 ERROR 🛑)
    print("""# END OF CHECK - Range for FilterDiameter must not be negative """)


    print("""# CHECK - Range for KOHDigestionTemp_c is 0 to 100 """)
    # CHECK - Range for KOHDigestionTemp_c is 0 to 100 (🟡 WARNING 🟡)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    invalid_temp = sampleextraction[
        (sampleextraction['kohdigestiontemp_c'] <= 0) | 
        (sampleextraction['kohdigestiontemp_c'] >= 100)
    ].tmp_row.tolist()

    warnings.append(
        checkData(
            tablename='tbl_mp_sampleextraction',
            badrows=invalid_temp,
            badcolumn='KOHDigestionTemp_c',
            error_type='Range Warning',
            error_message='KOHDigestionTemp_c should be between 0 and 100.'
        )
    )

    # END OF CHECK - Range for KOHDigestionTemp_c is 0 to 100 (🟡 WARNING 🟡)
    print("""# END OF CHECK - Range for KOHDigestionTemp_c is 0 to 100 """)


    print("""# CHECK - SieveMeshSize_um should be 125, 355, 500, or 5000 """)
    # CHECK - SieveMeshSize_um should be 125, 355, 500, 5000 (🟡 WARNING 🟡)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: 08/31/2023
    # Last Edited Coder: Robert Butler
    # NOTE (8/31/2023): updated sievemeshsizes according to Leah's requirements
    #                   this bight cycle analyzes different sizefractions than the original intercal study
    #                   sievemeshsizes are now 125, 355, 500, 5000

    invalid_mesh_size = sampleextraction[
        ~sampleextraction['sievemeshsize_um'].isin([125, 355, 500, 5000])
    ].tmp_row.tolist()

    warnings.append(
        checkData(
            tablename='tbl_mp_sampleextraction',
            badrows=invalid_mesh_size,
            badcolumn='SieveMeshSize_um',
            error_type='Value Warning',
            error_message='SieveMeshSize_um should be 125, 355, 500, or 5000 in most cases.'
        )
    )

    # END OF CHECK - SieveMeshSize_um should be 125, 355, 500, 5000 (🟡 WARNING 🟡)
    print("""# END OF CHECK - SieveMeshSize_um should be 125, 355, 500, or 5000 """)



    print("""# CHECK - SieveMeshSize_um must  be greater than zero """)
    # CHECK - SieveMeshSize_um must  be greater than zero (🛑 ERROR 🛑)
    # Created Coder: Robert Butler 
    # Created Date: 9/1/2023
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (9/1/2023): NA

    invalid_mesh_size = sampleextraction[ sampleextraction['sievemeshsize_um'] <= 0 ].tmp_row.tolist()

    errs.append(
        checkData(
            tablename='tbl_mp_sampleextraction',
            badrows=invalid_mesh_size,
            badcolumn='SieveMeshSize_um',
            error_type='Value Warning',
            error_message='SieveMeshSize_um must be greater than zero'
        )
    )

    # END OF CHECK - SieveMeshSize_um must  be greater than zero (🛑 ERROR 🛑)
    print("""# END OF CHECK - SieveMeshSize_um must  be greater than zero 5000 """)



    print("""# CHECK - if "time" < 0 it must be -88 """)
    # CHECK - if "time" < 0 it must be -88 (🛑 ERROR 🛑)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    invalid_time_value = sampleextraction[
        (sampleextraction['timehours'] < 0) & 
        (sampleextraction['timehours'] != -88)
    ].tmp_row.tolist()

    errs.append(
        checkData(
            tablename='tbl_mp_sampleextraction',
            badrows=invalid_time_value,
            badcolumn='timehours',
            error_type='Value Error',
            error_message='If "timehours" < 0, it must be -88 (indicating a missing value).'
        )
    )

    # END OF CHECK - if "timehours" < 0 it must be -88 (🛑 ERROR 🛑)
    print("""# END OF CHECK - if "timehours" < 0 it must be -88 """)


    print("""# CHECK - "timehours" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes """)
    # CHECK - "timehours" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    time_in_minutes = sampleextraction[
        sampleextraction['timehours'] > 15
    ].tmp_row.tolist()

    warnings.append(
        checkData(
            tablename='tbl_mp_sampleextraction',
            badrows=time_in_minutes,
            badcolumn='timehours',
            error_type='Range Warning',
            error_message='"timehours" should be in hours. Be sure to not report in minutes.'
        )
    )

    # END OF CHECK - "timehours" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    print("""# END OF CHECK - "timehours" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes """)

    

    print("""# CHECK - KOHDigestionTime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes """)
    # CHECK - KOHDigestionTime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)

    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    koh_time_warning = sampleextraction[
        sampleextraction['kohdigestiontime_hours'] > 15
    ].tmp_row.tolist()

    warnings.append(
        checkData(
            tablename='tbl_mp_sampleextraction',
            badrows=koh_time_warning,
            badcolumn='kohdigestiontime_hours',
            error_type='Range Warning',
            error_message='KOHDigestionTime_hours should be in hours. Double check your value to ensure it is not reported in minutes.'
        )
    )

    # END CHECK - KOHDigestionTime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    print("""# END OF CHECK - KOHDigestionTime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes """)
    


    
    print("""# CHECK - b1separationtime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes """)
    # CHECK - b1separationtime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)

    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    time_warning = sampleextraction[
        sampleextraction['b1separationtime_hours'] > 15
    ].tmp_row.tolist()

    warnings.append(
        checkData(
            tablename='tbl_mp_sampleextraction',
            badrows=time_warning,
            badcolumn='b1separationtime_hours',
            error_type='Range Warning',
            error_message='b1separationtime_hours should be in hours. Double check your value to be sure it is not reported in minutes.'
        )
    )

    # END CHECK - b1separationtime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    print("""# END OF CHECK - b1separationtime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes """)
    
    

    print("""# CHECK - b2separationtime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes """)
    # CHECK - b2separationtime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)

    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    time_warning = sampleextraction[
        sampleextraction['b2separationtime_hours'] > 15
    ].tmp_row.tolist()

    warnings.append(
        checkData(
            tablename='tbl_mp_sampleextraction',
            badrows=time_warning,
            badcolumn='b2separationtime_hours',
            error_type='Range Warning',
            error_message='b2separationtime_hours should be in hours. Do not report in minutes.'
        )
    )

    # END CHECK - b2separationtime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    print("""# END OF CHECK - b2separationtime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes """)



    print("""# CHECK - FilterPoreSize should be 1, 10, 20, or 50 """)
    # CHECK - FilterPoreSize should be 1, 10, 20, or 50 (🟡 WARNING 🟡)
    
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    invalid_pore_size_range = sampleextraction[~sampleextraction['filterporesize_um'].isin([1,10,20,50])].tmp_row.tolist()

    warnings.append(
        checkData(
            tablename='tbl_mp_sampleextraction',
            badrows=invalid_pore_size_range,
            badcolumn='filterporesize_um',
            error_type='Range Warning',
            error_message='FilterPoreSize should be 1, 10, 20, or 50.'
        )
    )

    # END CHECK - FilterPoreSize should be 1, 10, 20, or 50 (🟡 WARNING 🟡)
    print("""# END OF CHECK - FilterPoreSize should be 1, 10, 20, or 50 """)
   




    print("""# CHECK - if filterholder is "Other" then the "comments" field cannot be left blank """)
    # CHECK - if filterholder is "Other" then the "comments" field cannot be left blank (🛑 ERROR 🛑)

    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    missing_comments = sampleextraction[
        (sampleextraction['filterholder'] == "Other") & 
        (sampleextraction['comments'].fillna('').astype(str).str.replace("\s*","", regex = True) == '')
    ].tmp_row.tolist()

    errs.append(
        checkData(
            tablename='tbl_mp_sampleextraction',
            badrows=missing_comments,
            badcolumn='comments',
            error_type='Value Error',
            error_message='If filterholder is "Other", the "comments" field cannot be left blank.'
        )
    )

    print("""# END OF CHECK - if filterholder is "Other" then the "comments" field cannot be left blank """)





    ###############################################################################################################################################
    # ------------------------------------------------------------------------------------------------------------------------------------------- #
    # ---------------------------------------------------- END OF SampleExtraction Tab Checks --------------------------------------------------- #
    # ------------------------------------------------------------------------------------------------------------------------------------------- #
    ###############################################################################################################################################








    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #








    ###############################################################################################################################################
    # ------------------------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------------ SampleReceiving Tab Checks --------------------------------------------------------- #
    # ------------------------------------------------------------------------------------------------------------------------------------------- #
    ###############################################################################################################################################


    print("""# CHECK - DateReceived should not be before July 2023, and should not be a future date""")
    # CHECK - DateReceived should not be before July 2023, and should not be a future date (🛑 ERROR 🛑)

    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    
    # Define the start date as July 2023
    start_date = datetime(2023, 7, 1)

    # Current date
    current_date = datetime.today()

    invalid_dates = samplereceiving[
        (samplereceiving['datereceived'] < start_date) | 
        (samplereceiving['datereceived'] > current_date)
    ].tmp_row.tolist()

    errs.append(
        checkData(
            tablename='tbl_mp_samplereceiving',
            badrows=invalid_dates,
            badcolumn='datereceived',
            error_type='Date Error',
            error_message='DateReceived should not be before July 2023 and should not be a future date.'
        )
    )



    # END OF CHECK - DateReceived should not be before July 2023, and should not be a future date (🛑 ERROR 🛑)
    print("""# END OF CHECK - DateReceived should not be before July 2023, and should not be a future date""")


    ###############################################################################################################################################
    # ------------------------------------------------------------------------------------------------------------------------------------------- #
    # ---------------------------------------------------- END OF SampleReceiving Tab Checks ---------------------------------------------------- #
    # ------------------------------------------------------------------------------------------------------------------------------------------- #
    ###############################################################################################################################################








    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #








    ##################################################################################################################################################
    # ---------------------------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------------ MicroscopySettings Tab Checks --------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------------------------------------- #
    ##################################################################################################################################################




    print("""# CHECK - if "timehours" < 0 it must be -88""")
    # CHECK - if "timehours" < 0 it must be -88 (🛑 ERROR 🛑)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    invalid_times = microscopy[microscopy["timehours"] < 0 & (microscopy["timehours"] != -88)].tmp_row.tolist()
    errs.append(
        checkData(
            tablename='tbl_mp_microscopysettings',
            badrows=invalid_times,
            badcolumn='timehours',
            error_type='Value Error',
            error_message='Time should not be negative unless it is -88 indicating a missing value.'
        )
    )
    # END OF CHECK - if "timehours" < 0 it must be -88 (🛑 ERROR 🛑)
    print("""# END OF CHECK - if "timehours" < 0 it must be -88""")


    print("""# CHECK - "timehours" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes""")
    # CHECK - "timehours" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    time_warnings = microscopy[microscopy["timehours"] > 15].tmp_row.tolist()
    warnings.append(
        checkData(
            tablename='tbl_mp_microscopysettings',
            badrows=time_warnings,
            badcolumn='timehours',
            error_type='Time Format Warning',
            error_message='"timehours" > 15. Ensure values are reported in hours, not minutes.'
        )
    )

    # END OF CHECK - "timehours" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    print("""# END OF CHECK - "timehours" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes""")


    print("""# CHECK - Magnification should be between 1 and 1000""")
    # CHECK - Magnification should be between 1 and 1000 (🟡 WARNING 🟡)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    invalid_magnifications = microscopy[(microscopy["magnification"] < 1) | (microscopy["magnification"] > 1000)].tmp_row.tolist()
    warnings.append(
        checkData(
            tablename='tbl_mp_microscopysettings',
            badrows=invalid_magnifications,
            badcolumn='magnification',
            error_type='Value Warning',
            error_message='Magnification should be between 1 and 1000.'
        )
    )

    # END OF CHECK - Magnification should be between 1 and 1000 (🟡 WARNING 🟡)
    print("""# END OF CHECK - Magnification should be between 1 and 1000""")





    ##################################################################################################################################################
    # ---------------------------------------------------------------------------------------------------------------------------------------------- #
    # ---------------------------------------------------- END OF MicroscopySettings Tab Checks ---------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------------------------------------- #
    ##################################################################################################################################################








    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #








    ##################################################################################################################################################
    # ---------------------------------------------------------------------------------------------------------------------------------------------- #
    # --------------------------------------------------------- FTIRSettings Tab Checks ------------------------------------------------------------ #
    # ---------------------------------------------------------------------------------------------------------------------------------------------- #
    ##################################################################################################################################################



    print("""# CHECK - SpectralRange should have a format of 'NUMBER-NUMBER' """)
    # CHECK - SpectralRange should have a format of "NUMBER-NUMBER" (Use regular expressions) 
    #       (For example, a good value in this column should look something like "185-3400")
    # (🛑 ERROR 🛑)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    invalid_format = ftir[~ftir["spectralrange_cm"].fillna('').astype(str).str.match(r'^\d+-\d+$')].tmp_row.tolist()
    errs.append(
        checkData(
            tablename='tbl_mp_ftirsettings',
            badrows=invalid_format,
            badcolumn='SpectralRange_cm',
            error_type='Format Error',
            error_message='SpectralRange_cm should have a format of "NUMBER-NUMBER".'
        )
    )

    # END OF CHECK - SpectralRange should have a format of "NUMBER-NUMBER" (Use regular expressions) 
    #       (For example, a good value in this column should look something like "185-3400")
    # (🛑 ERROR 🛑)
    print("""# END OF CHECK - SpectralRange should have a format of 'NUMBER-NUMBER' """)

    # only run if above check passed
    if len(invalid_format) == 0:
        print("""# CHECK - SpectralRange min value should not be less than 0""")
        # CHECK - SpectralRange min value should not be less than 0 (🛑 ERROR 🛑)
        # Created Coder: Robert Butler (using ChatGPT)
        # Created Date: 08/28/23
        # Last Edited Date: NA
        # Last Edited Coder: NA
        # NOTE (MM/DD/YY): NA

        # Extracting min and max values
        ftir['min_value'] = ftir['spectralrange_cm'].fillna('').astype(str).str.split('-').str[0].astype(float)
        ftir['max_value'] = ftir['spectralrange_cm'].fillna('').astype(str).str.split('-').str[1].astype(float)

        print("""# CHECK - SpectralRange min value should not be less than 0""")
        invalid_min_values_below_0 = ftir[ftir["min_value"] < 0].tmp_row.tolist()
        errs.append(
            checkData(
                tablename='tbl_mp_ftirsettings',
                badrows=invalid_min_values_below_0,
                badcolumn='SpectralRange_cm',
                error_type='Value Error',
                error_message='SpectralRange_cm min value should not be less than 0.'
            )
        )

        # END OF CHECK - SpectralRange_cm min value should not be less than 0 (🛑 ERROR 🛑)
        print("""# END OF CHECK - SpectralRange_cm min value should not be less than 0""")


        print("""# CHECK - SpectralRange_cm min value should not be less than 400""")
        # CHECK - SpectralRange_cm min value should not be less than 400 (🟡 WARNING 🟡)
        # Created Coder: Robert Butler (using ChatGPT)
        # Created Date: 08/28/23
        # Last Edited Date: NA
        # Last Edited Coder: NA
        # NOTE (MM/DD/YY): NA
        warnings_below_400 = ftir[ftir["min_value"] < 400].tmp_row.tolist()
        warnings.append(
            checkData(
                tablename='tbl_mp_ftirsettings',
                badrows=warnings_below_400,
                badcolumn='SpectralRange_cm',
                error_type='Value Warning',
                error_message='SpectralRange_cm min value should not be less than 400.'
            )
        )

        # END OF CHECK - SpectralRange_cm min value should not be less than 400 (🟡 WARNING 🟡)
        print("""# END OF CHECK - SpectralRange_cm min value should not be less than 400""")


        print("""# CHECK - SpectralRange_cm max value should not be over 4000""")
        # CHECK - SpectralRange_cm max value should not be over 4000 (🟡 WARNING 🟡)
        # Created Coder: Robert Butler (using ChatGPT)
        # Created Date: 08/28/23
        # Last Edited Date: NA
        # Last Edited Coder: NA
        # NOTE (MM/DD/YY): NA
        warnings_above_4000 = ftir[ftir["max_value"] > 4000].tmp_row.tolist()
        warnings.append(
            checkData(
                tablename='tbl_mp_ftirsettings',
                badrows=warnings_above_4000,
                badcolumn='SpectralRange_cm',
                error_type='Value Warning',
                error_message='SpectralRange_cm max value should not be over 4000.'
            )
        )

        # END OF CHECK - SpectralRange_cm max value should not be over 4000 (🟡 WARNING 🟡)
        print("""# END OF CHECK - SpectralRange_cm max value should not be over 4000""")


        print("""# CHECK - SpectralRange_cm min value cannot be more than the max value""")
        # CHECK - SpectralRange_cm min value cannot be more than the max value (🛑 ERROR 🛑)
        # Created Coder: Robert Butler (using ChatGPT)
        # Created Date: 08/28/23
        # Last Edited Date: NA
        # Last Edited Coder: NA
        # NOTE (MM/DD/YY): NA
        invalid_min_values = ftir[ftir["min_value"] > ftir["max_value"]].tmp_row.tolist()
        errs.append(
            checkData(
                tablename='tbl_mp_ftirsettings',
                badrows=invalid_min_values,
                badcolumn='SpectralRange_cm',
                error_type='Value Error',
                error_message='SpectralRange_cm min value cannot be more than the max value.'
            )
        )

        # END OF CHECK - SpectralRange_cm min value cannot be more than the max value (🛑 ERROR 🛑)
        print("""# END OF CHECK - SpectralRange_cm min value cannot be more than the max value""")

        ftir.drop(['min_value', 'max_value'], inplace = True, axis = 'columns')



    print("""# CHECK - if "timehours" < 0 it must be -88 (🛑 ERROR 🛑)""")
    # CHECK - if "timehours" < 0 it must be -88 (🛑 ERROR 🛑)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    invalid_times = ftir[(ftir["timehours"] < 0) & (ftir["timehours"] != -88)].tmp_row.tolist()
    errs.append(
        checkData(
            tablename='tbl_mp_ftirsettings',
            badrows=invalid_times,
            badcolumn='timehours',
            error_type='Value Error',
            error_message='If "Time" is less than 0, it must be -88.'
        )
    )

    # END OF CHECK - if "timehours" < 0 it must be -88 (🛑 ERROR 🛑)
    print("""# END OF CHECK - if "timehours" < 0 it must be -88 (🛑 ERROR 🛑)""")


    print("""# CHECK - "timehours" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes""")
    # CHECK - "timehours" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    
    time_warnings = ftir[ftir["timehours"] > 15].tmp_row.tolist()
    warnings.append(
        checkData(
            tablename='tbl_mp_ftirsettings',
            badrows=time_warnings,
            badcolumn='timehours',
            error_type='Value Warning',
            error_message='"Time" must be measured in hours - it seems to be over 15, indicating it might be reported in minutes.'
        )
    )

    # END OF CHECK - "timehours" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    print("""# END OF CHECK - "timehours" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes""")


    print("""# CHECK - NumberScans should be greater than zero (🛑 ERROR 🛑)""")
    # CHECK - NumberScans should be greater than zero (🛑 ERROR 🛑)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: 08/28/23
    # Last Edited Coder: Robert Butler
    # NOTE (08/28/23): NumberScans should just be greater than zero

    errs.append(
        checkData(
            tablename='tbl_mp_ftirsettings',
            badrows=ftir[ftir.numberscans <= 0].tmp_row.tolist(), 
            badcolumn='NumberScans',
            error_type='Value Warning',
            error_message='NumberScans should be greater than zero.'  
        )
    )

    # END OF CHECK - NumberScans should be greater than zero (🛑 ERROR 🛑)
    print("""# END OF CHECK - NumberScans should be greater than zero (🛑 ERROR 🛑)""")




    ##################################################################################################################################################
    # ---------------------------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------------- END OF FTIRSettings Tab Checks ------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------------------------------------- #
    ##################################################################################################################################################








    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #








    ##################################################################################################################################################
    # ---------------------------------------------------------------------------------------------------------------------------------------------- #
    # --------------------------------------------------------- RamanSettings Tab Checks ------------------------------------------------------------ #
    # ---------------------------------------------------------------------------------------------------------------------------------------------- #
    ##################################################################################################################################################





    print("""# CHECK - Range for LaserWaveLength_nm is 500 to 800""")
    # CHECK - Range for LaserWaveLength_nm is 500 to 800 (🟡 WARNING 🟡)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    laser_wave_length_warnings = raman[(raman["laserwavelength_nm"] < 500) | (raman["laserwavelength_nm"] > 800)].tmp_row.tolist()
    warnings.append(
        checkData(
            tablename='tbl_mp_ramansettings',
            badrows=laser_wave_length_warnings,
            badcolumn='laserwavelength_nm',
            error_type='Value Warning',
            error_message='Range for LaserWaveLength_nm should be 500 to 800.'
        )
    )

    # END OF CHECK - Range for LaserWaveLength_nm is 500 to 800 (🟡 WARNING 🟡)
    print("""# END OF CHECK - Range for LaserWaveLength_nm is 500 to 800""")


    print("""# CHECK - Range for LaserGrating_nm is 200 to 4000""")
    # CHECK - Range for LaserGrating_nm is 200 to 4000 (🟡 WARNING 🟡)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    laser_grating_warnings = raman[(raman["lasergrating_nm"] < 200) | (raman["lasergrating_nm"] > 4000)].tmp_row.tolist()
    warnings.append(
        checkData(
            tablename='tbl_mp_ramansettings',
            badrows=laser_grating_warnings,
            badcolumn='lasergrating_nm',
            error_type='Value Warning',
            error_message='Range for LaserGrating_nm should be 200 to 4000.'
        )
    )
    # END OF CHECK - Range for LaserGrating_nm is 200 to 4000 (🟡 WARNING 🟡)
    print("""# END OF CHECK - Range for LaserGrating_nm is 200 to 4000""")


    print("""# CHECK - SpectralRange should have a format of 'NUMBER-NUMBER' (Use regular expressions) """)
    # CHECK - SpectralRange should have a format of "NUMBER-NUMBER" (Use regular expressions) 
    #       (For example, a good value in this column should look something like "185-3400") 
    # (🛑 ERROR 🛑)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    pattern = re.compile(r'^\d+-\d+$')
    invalid_spectral_range = raman[~raman["spectralrange_cm"].fillna('').astype(str).str.match(pattern)].tmp_row.tolist()
    errs.append(
        checkData(
            tablename='tbl_mp_ramansettings',
            badrows=invalid_spectral_range,
            badcolumn='spectralrange_cm',
            error_type='Value Error',
            error_message='SpectralRange should have a format of "NUMBER-NUMBER", e.g., "185-3400".'
        )
    )

    # END OF CHECK - SpectralRange should have a format of "NUMBER-NUMBER" (Use regular expressions) 
    #       (For example, a good value in this column should look something like "185-3400")
    # (🛑 ERROR 🛑)
    print("""# END OF CHECK - SpectralRange should have a format of 'NUMBER-NUMBER' """)

    if len(invalid_spectral_range) == 0:
        # Split the spectral range into min and max columns for easier processing
        raman['min_spectral_range'] = raman['spectralrange_cm'].fillna('').astype(str).str.split('-').str[0].astype(int)
        raman['max_spectral_range'] = raman['spectralrange_cm'].fillna('').astype(str).str.split('-').str[1].astype(int)

        print("""# CHECK - SpectralRange min value should not be less than 0""")
        # CHECK - SpectralRange min value should not be less than 0 (🛑 ERROR 🛑)
        # Created Coder: Robert Butler (using ChatGPT)
        # Created Date: 08/28/23
        # Last Edited Date: NA
        # Last Edited Coder: NA
        # NOTE (MM/DD/YY): NA
        min_val_below_zero = raman[raman['min_spectral_range'] < 0].tmp_row.tolist()
        errs.append(
            checkData(
                tablename='tbl_mp_ramansettings',
                badrows=min_val_below_zero,
                badcolumn='spectralrange_cm',
                error_type='Value Error',
                error_message='SpectralRange min value should not be less than 0.'
            )
        )
        # END OF CHECK - SpectralRange min value should not be less than 0 (🛑 ERROR 🛑)
        print("""# END OF CHECK - SpectralRange min value should not be less than 0""")

        print("""# CHECK - SpectralRange min value should not be less than 50""")
        # CHECK - SpectralRange min value should not be less than 50 (🟡 WARNING 🟡)
        # Created Coder: Robert Butler (using ChatGPT)
        # Created Date: 08/28/23
        # Last Edited Date: NA
        # Last Edited Coder: NA
        # NOTE (MM/DD/YY): NA
        min_val_below_50 = raman[raman['min_spectral_range'] < 50].tmp_row.tolist()
        warnings.append(
            checkData(
                tablename='tbl_mp_ramansettings',
                badrows=min_val_below_50,
                badcolumn='spectralrange_cm',
                error_type='Value Warning',
                error_message='SpectralRange min value should not be less than 50.'
            )
        )
        # END OF CHECK - SpectralRange min value should not be less than 50 (🟡 WARNING 🟡)
        print("""# END OF CHECK - SpectralRange min value should not be less than 50""")

        print("""# CHECK - SpectralRange max value should not be over 4000""")
        # CHECK - SpectralRange max value should not be over 4000 (🟡 WARNING 🟡)
        # Created Coder: Robert Butler (using ChatGPT)
        # Created Date: 08/28/23
        # Last Edited Date: NA
        # Last Edited Coder: NA
        # NOTE (MM/DD/YY): NA
        max_val_over_4000 = raman[raman['max_spectral_range'] > 4000].tmp_row.tolist()
        warnings.append(
            checkData(
                tablename='tbl_mp_ramansettings',
                badrows=max_val_over_4000,
                badcolumn='spectralrange_cm',
                error_type='Value Warning',
                error_message='SpectralRange max value should not be over 4000.'
            )
        )
        # END OF CHECK - SpectralRange max value should not be over 4000 (🟡 WARNING 🟡)
        print("""# END OF CHECK - SpectralRange max value should not be over 4000""")

        print("""# CHECK - SpectralRange min value cannot be more than the max value""")
        # CHECK - SpectralRange min value cannot be more than the max value (🛑 ERROR 🛑)
        # Created Coder: Robert Butler (using ChatGPT)
        # Created Date: 08/28/23
        # Last Edited Date: NA
        # Last Edited Coder: NA
        # NOTE (MM/DD/YY): NA
        min_more_than_max = raman[raman['min_spectral_range'] > raman['max_spectral_range']].tmp_row.tolist()
        errs.append(
            checkData(
                tablename='tbl_mp_ramansettings',
                badrows=min_more_than_max,
                badcolumn='spectralrange_cm',
                error_type='Value Error',
                error_message='SpectralRange min value cannot be more than the max value.'
            )
        )
        # END OF CHECK - SpectralRange min value cannot be more than the max value (🛑 ERROR 🛑)
        print("""# END OF CHECK - SpectralRange min value cannot be more than the max value""")

        # After all checks, drop the temporary columns created
        raman.drop(columns=['min_spectral_range', 'max_spectral_range'], inplace=True, errors='ignore')



    print("""# CHECK - Aperture should have a format of "NUMBER-NUMBER" (Use regular expressions) """)
    # CHECK - Aperture should have a format of "NUMBER-NUMBER" (Use regular expressions) 
    #       (For example, a good value in this column should look something like "100-150")
    # (🛑 ERROR 🛑)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    invalid_aperture_format = raman[~raman['aperture'].fillna('').astype(str).str.match(r'^\d+-\d+$')].tmp_row.tolist()
    errs.append(
        checkData(
            tablename='tbl_mp_ramansettings',
            badrows=invalid_aperture_format,
            badcolumn='Aperture',
            error_type='Value Error',
            error_message='Aperture should have a format of "NUMBER-NUMBER".'
        )
    )
    # END OF CHECK - Aperture should have a format of "NUMBER-NUMBER" (Use regular expressions) 
    #       (For example, a good value in this column should look something like "100-150")
    # (🛑 ERROR 🛑)
    print("""# END OF CHECK - Aperture should have a format of "NUMBER-NUMBER" (Use regular expressions) """)

    # Check if the above check has passed
    if not invalid_aperture_format:
        # Split the Aperture into min and max columns for easier processing
        raman['min_aperture'] = raman['aperture'].fillna('').astype(str).str.split('-').str[0].astype(int)
        raman['max_aperture'] = raman['aperture'].fillna('').astype(str).str.split('-').str[1].astype(int)

        print("""# CHECK - Aperture minimum value cannot be more than the max value""")
        # CHECK - Aperture minimum value cannot be more than the max value (🛑 ERROR 🛑)
        # Created Coder: Robert Butler (using ChatGPT)
        # Created Date: 08/28/23
        # Last Edited Date: NA
        # Last Edited Coder: NA
        # NOTE (MM/DD/YY): NA
        aperture_min_more_than_max = raman[raman['min_aperture'] > raman['max_aperture']].tmp_row.tolist()
        errs.append(
            checkData(
                tablename='tbl_mp_ramansettings',
                badrows=aperture_min_more_than_max,
                badcolumn='Aperture',
                error_type='Value Error',
                error_message='Aperture minimum value cannot be more than the max value.'
            )
        )
        # END OF CHECK - Aperture minimum value cannot be more than the max value (🛑 ERROR 🛑)
        print("""# END OF CHECK - Aperture minimum value cannot be more than the max value""")

        print("""# CHECK - Aperture minimum value cannot be less than 0""")
        # CHECK - Aperture minimum value cannot be less than 0 (🛑 ERROR 🛑)
        # Created Coder: Robert Butler (using ChatGPT)
        # Created Date: 08/28/23
        # Last Edited Date: NA
        # Last Edited Coder: NA
        # NOTE (MM/DD/YY): NA
        aperture_min_below_zero = raman[raman['min_aperture'] < 0].tmp_row.tolist()
        errs.append(
            checkData(
                tablename='tbl_mp_ramansettings',
                badrows=aperture_min_below_zero,
                badcolumn='Aperture',
                error_type='Value Error',
                error_message='Aperture minimum value cannot be less than 0.'
            )
        )
        # END OF CHECK - Aperture minimum value cannot be less than 0 (🛑 ERROR 🛑)
        print("""# END OF CHECK - Aperture minimum value cannot be less than 0""")

        # Drop the temporary columns created
        raman.drop(columns=['min_aperture', 'max_aperture'], inplace=True, errors='ignore')



    print("""# CHECK - Objective should be an integer 1 to 100""")
    # CHECK - Objective should be an integer 1 to 100 (🟡 WARNING 🟡)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    invalid_objective = raman[(raman['objective'] < 1) | (raman['objective'] > 100) ].tmp_row.tolist()
    warnings.append(
        checkData(
            tablename='tbl_mp_ramansettings',
            badrows=invalid_objective,
            badcolumn='Objective',
            error_type='Value Warning',
            error_message='Objective should be an integer 1 to 100.'
        )
    )
    # END OF CHECK - Objective should be an integer 1 to 100 (🟡 WARNING 🟡)
    print("""# END OF CHECK - Objective should be an integer 1 to 100""")

    print("""# CHECK - MatchThreshold should be a number from 0 to 100 since it is a percentage""")
    # CHECK - MatchThreshold should be a number from 0 to 100 since it is a percentage (🛑 ERROR 🛑)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    invalid_match_threshold = raman[(raman['matchthreshold'] < 0) | (raman['matchthreshold'] > 100)].tmp_row.tolist()
    errs.append(
        checkData(
            tablename='tbl_mp_ramansettings',
            badrows=invalid_match_threshold,
            badcolumn='MatchThreshold',
            error_type='Value Error',
            error_message='MatchThreshold should be a number from 0 to 100 since it is a percentage.'
        )
    )
    # END OF CHECK - MatchThreshold should be a number from 0 to 100 since it is a percentage (🛑 ERROR 🛑)
    print("""# END OF CHECK - MatchThreshold should be a number from 0 to 100 since it is a percentage""")

    print("""# CHECK - if "timehours" < 0 it must be -88""")
    # CHECK - if "timehours" < 0 it must be -88 (🛑 ERROR 🛑)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    invalid_time_negative = raman[(raman['timehours'] < 0) & (raman['timehours'] != -88)].tmp_row.tolist()
    errs.append(
        checkData(
            tablename='tbl_mp_ramansettings',
            badrows=invalid_time_negative,
            badcolumn='timehours',
            error_type='Value Error',
            error_message='If "timehours" < 0, it must be -88.'
        )
    )
    # END OF CHECK - if "timehours" < 0 it must be -88 (🛑 ERROR 🛑)
    print("""# END OF CHECK - if "timehours" < 0 it must be -88""")

    print("""# CHECK - "timehours" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes""")
    # CHECK - "timehours" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    # Created Coder: Robert Butler (using ChatGPT)
    # Created Date: 08/28/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    time_warning_rows = raman[raman['timehours'] > 15].tmp_row.tolist()
    warnings.append(
        checkData(
            tablename='tbl_mp_ramansettings',
            badrows=time_warning_rows,
            badcolumn='timehours',
            error_type='Value Warning',
            error_message='"timehours" must be measured in hours. Values over 15 suggest it might be reported in minutes.'
        )
    )
    # END OF CHECK - "timehours" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    print("""# END OF CHECK - "timehours" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes""")






    ##################################################################################################################################################
    # ---------------------------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------------- END OF RamanSettings Tab Checks ------------------------------------------------------ #
    # ---------------------------------------------------------------------------------------------------------------------------------------------- #
    ##################################################################################################################################################



    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #

    

    # End of Microplastics Custom Checks
    print("# --- End of Microplastics Custom Checks --- #")



    return {'errors': errs, 'warnings': warnings}
    



