# Dont touch this file! This is intended to be a template for implementing new custom checks
from inspect import currentframe
from flask import current_app, g, session
from .functions import checkData, mismatch, check_microscopy_instrument_settings
import pandas as pd
import os

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
    labinfo = all_dfs.get('tbl_mp_labinfo')
    instrumentinfo = all_dfs.get('tbl_mp_instrumentinfo')
    microscopy = all_dfs.get('tbl_mp_microscopysettings')
    raman = all_dfs.get('tbl_mp_ramansettings')
    ftir = all_dfs.get('tbl_mp_ftirsettings')
    results = all_dfs.get('tbl_mp_results')
    sampleextraction = all_dfs.get('tbl_mp_sampleextraction')
    samplereceiving = all_dfs.get('tbl_mp_samplereceiving')

    labinfo['tmp_row'] = labinfo.index
    instrumentinfo['tmp_row'] = instrumentinfo.index
    microscopy['tmp_row'] = microscopy.index
    raman['tmp_row'] = raman.index
    ftir['tmp_row'] = ftir.index
    results['tmp_row'] = results.index
    sampleextraction['tmp_row'] = sampleextraction.index
    samplereceiving['tmp_row'] = samplereceiving.index

    args = {
        "dataframe": pd.DataFrame(),
        "tablename": "",
        "badrows": [],
        "badcolumn": "",
        "error_type": "",
        "is_core_error": False,
        "error_message": ""
    }
    
    labinfo_args = args.update({
        "dataframe": labinfo,
        "tablename": "tbl_mp_labinfo"
    })
    instrumentinfo_args = args.update({
        "dataframe": instrumentinfo,
        "tablename": "tbl_mp_instrumentinfo"
    })
    microscopy_args = args.update({
        "dataframe": microscopy,
        "tablename": "tbl_mp_microscopysettings"
    })
    raman_args = args.update({
        "dataframe": raman,
        "tablename": "tbl_mp_ramansettings"
    })
    ftir_args = args.update({
        "dataframe": ftir,
        "tablename": "tbl_mp_ftirsettings"
    })
    results_args = args.update({
        "dataframe": results,
        "tablename": "tbl_mp_results"
    })
    samplereceiving_args = args.update({
        "dataframe": samplereceiving,
        "tablename": "tbl_mp_samplereceiving"
    })
    sampleextraction_args = args.update({
        "dataframe": sampleextraction,
        "tablename": "tbl_mp_sampleextraction"
    })



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
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    uploaded_photoids = os.listdir(session['submission_photos_dir'])

    args.update({
        "dataframe": results,
        "tablename": "tbl_mp_results",
        "badrows": results[~results['photoid'].isin(uploaded_photoids)].tmp_row.tolist(), 
        "badcolumn": "photoid",
        "error_type": "Logic Error",
        "error_message": "PhotoID of tbl_mp_results tab must have a matching uploaded photo"
    })
    errs = [*errs, checkData(**args)]

    # END OF CHECK - PhotoID of tbl_mp_results tab must have a matching uploaded photo (🛑 ERROR 🛑)
    print("# END OF CHECK - PhotoID of tbl_mp_results tab must have a matching uploaded photo")


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
        args.update({
            "dataframe": results,
            "tablename": "tbl_mp_results",
            "badrows": results.tmp_row.tolist(), 
            "badcolumn": "photoid",
            "error_type": "Logic Error",
            "error_message": "All uploaded photos must have a matching PhotoID in tbl_mp_results tab"
        })
        errs = [*errs, checkData(**args)]


    # END OF CHECK - Photo uploaded must match their submission (PhotoID column in the tbl_mp_results tab) (🛑 ERROR 🛑)
    print("# END OF CHECK - Photo uploaded must match their submission (PhotoID column in the tbl_mp_results tab)")


    print("# CHECK - Cannot upload a photo with a filename that matches one that was previously used in a previous submission")
    # Description - Cannot upload a photo with a filename that matches one that was previously used in a previous submission (🛑 ERROR 🛑)
    # Created Coder: Nick Lombardo
    # Created Date: 08/22/23
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA

    unique_photoids = pd.read_sql('SELECT DISTINCT photoid from tbl_mp_results', g.eng)

    args.update({
        "dataframe": results,
        "tablename": "tbl_mp_results",
        "badrows": results[results['photoid'].isin(unique_photoids)].tmp_row.tolist(), 
        "badcolumn": "photoid",
        "error_type": "Logic Error",
        "error_message": "PhotoID of tbl_mp_results tab must have a matching uploaded photo"
    })
    errs = [*errs, checkData(**args)]

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
    # Last Edited Date: NA
    # Last Edited Coder: NA
    # NOTE (MM/DD/YY): NA
    
    if not results[results['raman'] == 'Yes'].empty:
        args.update({
            "dataframe": results,
            "tablename": "tbl_mp_results",
            "badrows": check_microscopy_instrument_settings('raman', results, raman), 
            "badcolumn": "raman",
            "error_type": "Logic Error",
            "error_message": "There must be a corresponding record in the ramansettings table"
        })
        errs = [*errs, checkData(**args)]


    # END OF CHECK - If Raman = 'Yes' (in results table) then there must be a corresponding record in the ramansettings table 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    print("# END OF CHECK - If Raman = 'Yes' (in results table) then there must be a corresponding record in the ramansettings table ")



    print("# CHECK - If FTIR = 'Yes' (in results table) then there must be a corresponding record in the ftirsettings table ")
    # CHECK - If FTIR = 'Yes' (in results table) then there must be a corresponding record in the ftirsettings table 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    
    if not results[results['ftir'] == 'Yes'].empty:
        args.update({
            "dataframe": results,
            "tablename": "tbl_mp_results",
            "badrows": check_microscopy_instrument_settings('ftir', results, ftir), 
            "badcolumn": "ftir",
            "error_type": "Logic Error",
            "error_message": "There must be a corresponding record in the ftirsettings table"
        })
        errs = [*errs, checkData(**args)]


    # END OF CHECK - If FTIR = 'Yes' (in results table) then there must be a corresponding record in the ftirsettings table 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    print("# END OF CHECK - If FTIR = 'Yes' (in results table) then there must be a corresponding record in the ftirsettings table ")
    



    print("# CHECK - If stereoscope = 'Yes' (in results table) then there must be a corresponding record in the microscopysettings table ")
    # CHECK - If stereoscope = 'Yes' (in results table) then there must be a corresponding record in the microscopysettings table 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    
    if not results[results['stereoscope'] == 'Yes'].empty:
        args.update({
            "dataframe": results,
            "tablename": "tbl_mp_results",
            "badrows": check_microscopy_instrument_settings('stereoscope', results, microscopy), 
            "badcolumn": "stereoscope",
            "error_type": "Logic Error",
            "error_message": "There must be a corresponding record in the microscopysettings table"
        })
        errs = [*errs, checkData(**args)]



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
    

    # Raman
    print("# Raman")

    # FTIR
    print("# FTIR")

    # Stereoscope
    print("# Stereoscope")

    # Other
    print("# Other")

    # END OF CHECKS - for each "instrument" column which says "Yes" in the results table, there must be a corresponding instrumentinfo record 
    #   (e.g. If Raman = "Yes" then...
    #           there must be a matching record in instrumentinfo where instrumenttype = 'Raman' which matches the record in the results table. 
    # (🛑 ERROR 🛑)
    print("""# END OF CHECKS - for each "instrument" column which says "Yes" in the results table, there must be a corresponding instrumentinfo record """)

    
    
    # ------- END OF Results <-----> InstrumentInfo ------- #




    # ------- Results <-----> SampleExtraction ------- #
    
    print("# CHECKS - Each record in Results must have a matching record in SampleExtraction (and vice versa)")
    # CHECKS - Each record in Results must have a matching record in SampleExtraction (and vice versa)
    #   Results Table matches SampleExtraction on  StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    
    # END CHECKS - Each record in Results must have a matching record in SampleExtraction (and vice versa)
    #   Results Table matches SampleExtraction on  StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    print("# END OF CHECKS - Each record in Results must have a matching record in SampleExtraction (and vice versa)")
    
    # ------- END Results <-----> SampleExtraction ------- #




    # ------- Results <-----> SampleReceiving ------- #
    
    print("# CHECKS - Each record in Results must have a matching record in SampleReceiving (and vice versa)")
    # CHECKS - Each record in Results must have a matching record in SampleReceiving (and vice versa)
    #   Results Table matches SampleReceiving on  StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)

    # END CHECKS - Each record in Results must have a matching record in SampleReceiving (and vice versa)
    #   Results Table matches SampleReceiving on  StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    print("# END CHECKS - Each record in Results must have a matching record in SampleReceiving (and vice versa)")
    
    # ------- END Results <-----> SampleReceiving ------- #




    # ------- Results <-----> LabInfo ------- #


    print("# CHECKS - Results Table matches Labinfo on StationID, SampleDate, Lab, Matrix (two ways)")
    # CHECKS - Results Table matches Labinfo on StationID, SampleDate, Lab, Matrix (two ways) (🛑 ERROR 🛑)

    # END CHECKS - Results Table matches Labinfo on StationID, SampleDate, Lab, Matrix (two ways) (🛑 ERROR 🛑)
    print("# END CHECKS - Results Table matches Labinfo on StationID, SampleDate, Lab, Matrix (two ways)")


    # ------- END Results <-----> LabInfo ------- #







    # ----------------------------- END Relating Results tab to the other tables ------------------------- #
    





    
    
    # ------------------------------- BEGIN Relating InstrumentInfo tab to the other tables --------------------------- #

    # ------- InstrumentInfo <-----> Settings tables ------- #


    print("# CHECK - If InstrumentType = 'Raman' (in instrumentinfo table) then there must be a corresponding record in the ramansettings table") 
    # CHECK - If InstrumentType = 'Raman' (in instrumentinfo table) then there must be a corresponding record in the ramansettings table 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    
    # END OF CHECK - If InstrumentType = 'Raman' (in instrumentinfo table) then there must be a corresponding record in the ramansettings table 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    print("# END OF CHECK - If InstrumentType = 'Raman' (in instrumentinfo table) then there must be a corresponding record in the ramansettings table")



    print("# CHECK - Record in ramanettings requires a corresponding record in InstrumentInfo where InstrumentType = 'Raman'")
    # CHECK - Record in ramanettings requires a corresponding record in InstrumentInfo where InstrumentType = 'Raman' 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    
    # END CHECK - Record in ramanettings requires a corresponding record in InstrumentInfo where InstrumentType = 'Raman' 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    print("# END CHECK - Record in ramanettings requires a corresponding record in InstrumentInfo where InstrumentType = 'Raman'")






    print("# CHECK - If InstrumentType = 'FTIR' (in instrumentinfo table) then there must be a corresponding record in the ftirsettings table")
    # CHECK - If InstrumentType = 'FTIR' (in instrumentinfo table) then there must be a corresponding record in the ftirsettings table 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    
    # END OF CHECK - If InstrumentType = 'FTIR' (in instrumentinfo table) then there must be a corresponding record in the ftirsettings table 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    print("# END OF CHECK - If InstrumentType = 'FTIR' (in instrumentinfo table) then there must be a corresponding record in the ftirsettings table")



    print("# CHECK - Record in ftirsettings requires a corresponding record in InstrumentInfo where InstrumentType = 'FTIR'")
    # CHECK - Record in ftirsettings requires a corresponding record in InstrumentInfo where InstrumentType = 'FTIR' 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    
    # END CHECK - Record in ftirsettings requires a corresponding record in InstrumentInfo where InstrumentType = 'FTIR' 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    print("# END CHECK - Record in ftirsettings requires a corresponding record in InstrumentInfo where InstrumentType = 'FTIR'")
    








    print("# CHECK - If InstrumentType = 'stereoscope' (in instrumentinfo table) then there must be a corresponding record in the microscopysettings table") 
    # CHECK - If InstrumentType = 'stereoscope' (in instrumentinfo table) then there must be a corresponding record in the microscopysettings table 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    
    # END OF CHECK - If InstrumentType = 'stereoscope' (in instrumentinfo table) then there must be a corresponding record in the microscopysettings table 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    print("# END OF CHECK - If InstrumentType = 'stereoscope' (in instrumentinfo table) then there must be a corresponding record in the microscopysettings table")
    



    print("# CHECK - Record in microscopysettings requires a corresponding record in InstrumentInfo where InstrumentType = 'stereoscope'")
    # CHECK - Record in microscopysettings requires a corresponding record in InstrumentInfo where InstrumentType = 'stereoscope' 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)

    # END CHECK - Record in microscopysettings requires a corresponding record in InstrumentInfo where InstrumentType = 'stereoscope' 
    #   Records must match on StationID, SampleDate, Lab, Matrix, SampleType, SizeFraction
    # (🛑 ERROR 🛑)
    print("# END CHECK - Record in microscopysettings requires a corresponding record in InstrumentInfo where InstrumentType = 'stereoscope'")
    


    # ------- END InstrumentInfo <-----> Settings tables ------- #






    # --------- InstrumentInfo <-----> SampleReceiving --------- #


    print("""# CHECK - InstrumentInfo Record must match SampleReceiving on Lab and Matrix (two ways)""")
    # CHECK - InstrumentInfo Record must match SampleReceiving on Lab and Matrix (two ways) (🛑 ERROR 🛑)

    # END CHECK - InstrumentInfo Record must match SampleReceiving on Lab and Matrix (two ways) (🛑 ERROR 🛑)
    print("""# END CHECK - InstrumentInfo Record must match SampleReceiving on Lab and Matrix (two ways)""")


    # ------- END InstrumentInfo <-----> SampleReceiving ------- #
    




    

    # --------- InstrumentInfo <-----> SampleExtraction --------- #
    
    print("""# CHECK - InstrumentInfo Record must match SampleExtraction on Lab and Matrix (two ways)""")
    # CHECK - InstrumentInfo Record must match SampleExtraction on Lab and Matrix (two ways) (🛑 ERROR 🛑)
    # END CHECK - InstrumentInfo Record must match SampleExtraction on Lab and Matrix (two ways) (🛑 ERROR 🛑)
    print("""# END CHECK - InstrumentInfo Record must match SampleExtraction on Lab and Matrix (two ways)""")
    
    # ------- END InstrumentInfo <-----> SampleExtraction ------- #


    # ----------------------------- END Relating InstrumentInfo tab to the other tables ------------------------- #






    # ---------------------------- Relating Sample Extraction to Sample Receiving ------------------------------- #

    print("""# SampleExtraction must match SampleReceiving on StationID, SampleDate, Lab, Matrix, SampleType (and Vice Versa)""")
    # SampleExtraction must match SampleReceiving on StationID, SampleDate, Lab, Matrix, SampleType (and Vice Versa) (🛑 ERROR 🛑)
    # END SampleExtraction must match SampleReceiving on StationID, SampleDate, Lab, Matrix, SampleType (and Vice Versa) (🛑 ERROR 🛑)
    print("""# END SampleExtraction must match SampleReceiving on StationID, SampleDate, Lab, Matrix, SampleType (and Vice Versa)""")
    
    # -------------------------- END Relating Sample Extraction to Sample Receiving ----------------------------- #



    # ---------------------------------------------------------------------------------------------------- #
    # -------------- END OF Traditional Logic Checks - Checking relationships between tables ------------- #
    # ---------------------------------------------------------------------------------------------------- #
    
    
    


    
    # ----------------------------------------------------------------------------------------------------- #
    # -------------------------- Sample Assignment Table Checks for Sediment Grabs ------------------------ #
    # ----------------------------------------------------------------------------------------------------- #






    print("""# CHECK - If matrix is sediment (In results table), check whether or not the lab was assigned Microplastics in the sample_assignment_table""")
    # CHECK - If matrix is sediment (In results table), check whether or not the lab was assigned Microplastics in the sample_assignment_table (🛑 ERROR 🛑)

    # END OF CHECK - If matrix is sediment (In results table), check whether or not the lab was assigned Microplastics in the sample_assignment_table (🛑 ERROR 🛑)
    print("# END OF CHECK - If matrix is sediment (In results table), check whether or not the lab was assigned Microplastics in the sample_assignment_table")




    print("""# CHECK - If matrix is sediment (In results table), check whether or not the stations submitted were assigned Field blanks""")
    # CHECK - If matrix is sediment (In results table), check whether or not the stations submitted were assigned Field blanks (🛑 ERROR 🛑)

    # END OF CHECK - If matrix is sediment (In results table), check whether or not the stations submitted were assigned Field blanks (🛑 ERROR 🛑)
    print("""# END OF CHECK - If matrix is sediment (In results table), check whether or not the stations submitted were assigned Field blanks""")




    print("""# CHECK - If we are doing Equipment blanks, each participating lab needs to submit one set of data for the Equipment blank""")
    # CHECK - If we are doing Equipment blanks, each participating lab needs to submit one set of data for the Equipment blank (🛑 ERROR 🛑)

    # END OF CHECK - If we are doing Equipment blanks, each participating lab needs to submit one set of data for the Equipment blank (🛑 ERROR 🛑)
    print("""# END OF CHECK - If we are doing Equipment blanks, each participating lab needs to submit one set of data for the Equipment blank""")







    # ----------------------------------------------------------------------------------------------------- #
    # ---------------------- END OF Sample Assignment Table Checks for Sediment Grabs --------------------- #
    # ----------------------------------------------------------------------------------------------------- #


    


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
    # CHECK - If the matrix is sediment, then the stationid must come from lu_station (stationid column) (🛑 ERROR 🛑)
    # END OF CHECK - If the matrix is sediment, then the stationid must come from lu_station (stationid column) (🛑 ERROR 🛑)
    print("""# END OF CHECK - If the matrix is sediment, then the stationid must come from lu_station (stationid column)""")


    print("""# CHECK - Moisture content should be an integer from 0 to 100""")
    # CHECK - Moisture content should be an integer from 0 to 100 (🛑 ERROR 🛑)
    # END OF CHECK - Moisture content should be an integer from 0 to 100 (🛑 ERROR 🛑)
    print("""# END OF CHECK - Moisture content should be an integer from 0 to 100""")


    print("""# CHECK - ParticleID should be unique in the results table. """)
    # CHECK - ParticleID should be unique in the results table. 
    #     Check for a duplicate particleID in their submission, and check if the same particleID name already exists in the results table in the database 
    # (🛑 ERROR 🛑)

    # END OF CHECK - ParticleID should be unique in the results table. 
    #     Check for a duplicate particleID in their submission, and check if the same particleID name already exists in the results table in the database 
    # (🛑 ERROR 🛑)
    print("""# END OF CHECK - ParticleID should be unique in the results table. """)



    print("""# CHECK - Length column should be from 0 to 5mm (non inclusive range)""")
    # CHECK - Length column should be from 0 to 5mm (non inclusive range) (🟡 WARNING 🟡)
    # END OF CHECK - Length column should be from 0 to 5mm (non inclusive range) (🟡 WARNING 🟡)
    print("""# END OF CHECK - Length column should be from 0 to 5mm (non inclusive range)""")


    print("""# CHECK - Width column shuold be from 0 to 5 mm (non inclusive range)""")
    # CHECK - Width column shuold be from 0 to 5 mm (non inclusive range) (🟡 WARNING 🟡)
    # END OF CHECK - Width column shuold be from 0 to 5 mm (non inclusive range) (🟡 WARNING 🟡)
    print("""# END OF CHECK - Width column shuold be from 0 to 5 mm (non inclusive range)""")


    print("""# CHECK - If Raman = 'Yes' Then raman_chemicalid cannot be 'not measured'""")
    # CHECK - If Raman = 'Yes' Then raman_chemicalid cannot be 'not measured' (🛑 ERROR 🛑)
    # END OF CHECK - If Raman = 'Yes' Then raman_chemicalid cannot be 'not measured' (🛑 ERROR 🛑)
    print("""# END OF CHECK - If Raman = 'Yes' Then raman_chemicalid cannot be 'not measured'""")


    print("""# CHECK - If FTIR = 'Yes' (in results table) then ftir_chemicalid cannot be 'not measured'""")
    # CHECK - If FTIR = 'Yes' (in results table) then ftir_chemicalid cannot be 'not measured' (🛑 ERROR 🛑)
    # END OF CHECK - If FTIR = 'Yes' (in results table) then ftir_chemicalid cannot be 'not measured' (🛑 ERROR 🛑)
    print("""# END OF CHECK - If FTIR = 'Yes' (in results table) then ftir_chemicalid cannot be 'not measured'""")


    print("""# CHECK - If SampleType is Lab blank or Equipment blank, then the StationID must be '0000'""")
    # CHECK - If SampleType is Lab blank or Equipment blank, then the StationID must be '0000' (🛑 ERROR 🛑)
    # END OF CHECK - If SampleType is Lab blank or Equipment blank, then the StationID must be '0000' (🛑 ERROR 🛑)
    print("""# END OF CHECK - If SampleType is Lab blank or Equipment blank, then the StationID must be '0000'""")


    print("""# CHECK - If SampleType is Result or Field blank, then the StationID must not be '0000'""")
    # CHECK - If SampleType is Result or Field blank, then the StationID must not be '0000' (🛑 ERROR 🛑)
    # END OF CHECK - If SampleType is Result or Field blank, then the StationID must not be '0000' (🛑 ERROR 🛑)
    print("""# END OF CHECK - If SampleType is Result or Field blank, then the StationID must not be '0000'""")


    print("""# CHECK - TimeImagesMeasurements must be in hours - warn if over __ saying that they should not report in minutes """)
    # CHECK - TimeImagesMeasurements must be in hours - warn if over __ saying that they should not report in minutes (🟡 WARNING 🟡)
    # END OF CHECK - TimeImagesMeasurements must be in hours - warn if over __ saying that they should not report in minutes (🟡 WARNING 🟡)
    print("""# END OF CHECK - TimeImagesMeasurements must be in hours - warn if over __ saying that they should not report in minutes """)


    print("""# CHECK - If TimeImagesMeasurements is less than 0, it must be -88 """)
    # CHECK - If TimeImagesMeasurements is less than 0, it must be -88 (🛑 ERROR 🛑)
    # END OF CHECK - If TimeImagesMeasurements is less than 0, it must be -88 (🛑 ERROR 🛑)
    print("""# END OF CHECK - If TimeImagesMeasurements is less than 0, it must be -88 """)


    print("""# CHECK - Other_InstrumentType must a value from lu_instrumenttype, but must not be "FTIR", "Raman", or "Stereoscope" """)
    # CHECK - Other_InstrumentType must a value from lu_instrumenttype, but must not be "FTIR", "Raman", or "Stereoscope" (🛑 ERROR 🛑)
    # END OF CHECK - Other_InstrumentType must a value from lu_instrumenttype, but must not be "FTIR", "Raman", or "Stereoscope" (🛑 ERROR 🛑)
    print("""# END OF CHECK - Other_InstrumentType must a value from lu_instrumenttype, but must not be "FTIR", "Raman", or "Stereoscope" """)


    print("""# CHECK - If "Other" = 'Yes' then "Other_InstrumentType" must not be left blank """)
    # CHECK - If "Other" = 'Yes' then "Other_InstrumentType" must not be left blank (🛑 ERROR 🛑)
    # END OF CHECK - If "Other" = 'Yes' then "Other_InstrumentType" must not be left blank (🛑 ERROR 🛑)
    print("""# END OF CHECK - If "Other" = 'Yes' then "Other_InstrumentType" must not be left blank """)


    print("""# CHECK - If "Other" = 'No' then Other_InstrumentType must be left blank """)
    # CHECK - If "Other" = 'No' then Other_InstrumentType must be left blank (🛑 ERROR 🛑)
    # END OF CHECK - If "Other" = 'No' then Other_InstrumentType must be left blank (🛑 ERROR 🛑)
    print("""# END OF CHECK - If "Other" = 'No' then Other_InstrumentType must be left blank """)






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
    # END OF CHECK - If instrumenttype = 'Other' then a comment is required (🛑 ERROR 🛑)
    print("""# END OF CHECK - If instrumenttype = 'Other' then a comment is required""")



    print("""# CHECK - Required Columns - 'SoftwareCollection', 'SoftwareProcessing', 'SoftwareMatching', 'SpectralLibraries', 'LibraryDetails', 'CalibrationFrequency' """)
    # CHECK - Required Columns - 'SoftwareCollection', 'SoftwareProcessing', 'SoftwareMatching', 'SpectralLibraries', 'LibraryDetails', 'CalibrationFrequency' 
    #       ***Unless the instrumenttype is "Other" or "Stereoscope"
    # (🛑 ERROR 🛑)

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





    print("""# CHECK - If AirFiltration is "Yes" then AirFiltrationType must not be empty """)
    # CHECK - If AirFiltration is "Yes" then AirFiltrationType must not be empty (🛑 ERROR 🛑)
    # END OF CHECK - If AirFiltration is "Yes" then AirFiltrationType must not be empty (🛑 ERROR 🛑)
    print("""# END OF CHECK - If AirFiltration is "Yes" then AirFiltrationType must not be empty """)



    print("""# CHECK - If AirFiltration is "No" Then AirFiltrationType must be empty """)
    # CHECK - If AirFiltration is "No" Then AirFiltrationType must be empty (🛑 ERROR 🛑)
    # END OF CHECK - If AirFiltration is "No" Then AirFiltrationType must be empty (🛑 ERROR 🛑)
    print("""# END OF CHECK - If AirFiltration is "No" Then AirFiltrationType must be empty """)



    print("""# CHECK - If SealedEnvironment is "Yes" then SealedEnvironmentType must not be empty """)
    # CHECK - If SealedEnvironment is "Yes" then SealedEnvironmentType must not be empty (🛑 ERROR 🛑)
    # END OF CHECK - If SealedEnvironment is "Yes" then SealedEnvironmentType must not be empty (🛑 ERROR 🛑)
    print("""# END OF CHECK - If SealedEnvironment is "Yes" then SealedEnvironmentType must not be empty """)



    print("""# CHECK - If SealedEnvironment is "No" Then SealedEnvironmentType must be empty """)
    # CHECK - If SealedEnvironment is "No" Then SealedEnvironmentType must be empty (🛑 ERROR 🛑)
    # END OF CHECK - If SealedEnvironment is "No" Then SealedEnvironmentType must be empty (🛑 ERROR 🛑)
    print("""# END OF CHECK - If SealedEnvironment is "No" Then SealedEnvironmentType must be empty """)



    print("""# CHECK - If ClothingPolicy is "Yes" then ClothingPolicyType must not be empty """)
    # CHECK - If ClothingPolicy is "Yes" then ClothingPolicyType must not be empty (🛑 ERROR 🛑)
    # END OF CHECK - If ClothingPolicy is "Yes" then ClothingPolicyType must not be empty (🛑 ERROR 🛑)
    print("""# END OF CHECK - If ClothingPolicy is "Yes" then ClothingPolicyType must not be empty """)



    print("""# CHECK - If ClothingPolicy is "No" Then ClothingPolicyType must be empty """)
    # CHECK - If ClothingPolicy is "No" Then ClothingPolicyType must be empty (🛑 ERROR 🛑)
    # END OF CHECK - If ClothingPolicy is "No" Then ClothingPolicyType must be empty (🛑 ERROR 🛑)
    print("""# END OF CHECK - If ClothingPolicy is "No" Then ClothingPolicyType must be empty """)



    print("""# CHECK - StartDate must not be before July 2023, nor after the date of their submission (today()) """)
    # CHECK - StartDate must not be before July 2023, nor after the date of their submission (today()) (🛑 ERROR 🛑)
    # END OF CHECK - StartDate must not be before July 2023, nor after the date of their submission (today()) (🛑 ERROR 🛑)
    print("""# END OF CHECK - StartDate must not be before July 2023, nor after the date of their submission (today()) """)



    print("""# CHECK - EndDate must not be before StartDate """)
    # CHECK - EndDate must not be before StartDate (🛑 ERROR 🛑)
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




    print("""# CHECK - Range for FilterPoreSize is 0 to 500 """)
    # CHECK - Range for FilterPoreSize is 0 to 500 (🟡 WARNING 🟡)
    # END OF CHECK - Range for FilterPoreSize is 0 to 500 (🟡 WARNING 🟡)
    print("""# END OF CHECK - Range for FilterPoreSize is 0 to 500 """)


    print("""# CHECK - Range for FilterDiameter is 0 to 100 """)
    # CHECK - Range for FilterDiameter is 0 to 100 (🟡 WARNING 🟡)
    # END OF CHECK - Range for FilterDiameter is 0 to 100 (🟡 WARNING 🟡)
    print("""# END OF CHECK - Range for FilterDiameter is 0 to 100 """)


    print("""# CHECK - Range for KOHDigestionTemp is 0 to 100 """)
    # CHECK - Range for KOHDigestionTemp is 0 to 100 (🟡 WARNING 🟡)
    # END OF CHECK - Range for KOHDigestionTemp is 0 to 100 (🟡 WARNING 🟡)
    print("""# END OF CHECK - Range for KOHDigestionTemp is 0 to 100 """)


    print("""# CHECK - SieveMeshSize should be 212 or 500 """)
    # CHECK - SieveMeshSize should be 212 or 500 (🟡 WARNING 🟡)
    # END OF CHECK - SieveMeshSize should be 212 or 500 (🟡 WARNING 🟡)
    print("""# END OF CHECK - SieveMeshSize should be 212 or 500 """)


    print("""# CHECK - if "time" < 0 it must be -88 """)
    # CHECK - if "time" < 0 it must be -88 (🛑 ERROR 🛑)
    # END OF CHECK - if "time" < 0 it must be -88 (🛑 ERROR 🛑)
    print("""# END OF CHECK - if "time" < 0 it must be -88 """)


    print("""# CHECK - "time" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes """)
    # CHECK - "time" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    # END OF CHECK - "time" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    print("""# END OF CHECK - "time" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes """)


    print("""# CHECK - KOHDigestionTime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes """)
    # CHECK - KOHDigestionTime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    # END OF CHECK - KOHDigestionTime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    print("""# END OF CHECK - KOHDigestionTime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes """)


    print("""# CHECK - B1SeparationTime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes """)
    # CHECK - B1SeparationTime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    # END OF CHECK - B1SeparationTime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    print("""# END OF CHECK - B1SeparationTime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes """)


    print("""# CHECK - B2SeparationTime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes """)
    # CHECK - B2SeparationTime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    # END OF CHECK - B2SeparationTime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    print("""# END OF CHECK - B2SeparationTime must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes """)


    print("""# CHECK - FilterPoreSize should be between ___ and ___ """)
    # CHECK - FilterPoreSize should be between ___ and ___ (🟡 WARNING 🟡)
    # END OF CHECK - FilterPoreSize should be between ___ and ___ (🟡 WARNING 🟡)
    print("""# END OF CHECK - FilterPoreSize should be between ___ and ___ """)


    print("""# CHECK - FilterDiameter should be between ___ and ___ """)
    # CHECK - FilterDiameter should be between ___ and ___ (🟡 WARNING 🟡)
    # END OF CHECK - FilterDiameter should be between ___ and ___ (🟡 WARNING 🟡)
    print("""# END OF CHECK - FilterDiameter should be between ___ and ___ """)


    print("""# CHECK - if filterholder is "Other" then the "comments" field cannot be left blank """)
    # CHECK - if filterholder is "Other" then the "comments" field cannot be left blank (🛑 ERROR 🛑)
    # END OF CHECK - if filterholder is "Other" then the "comments" field cannot be left blank (🛑 ERROR 🛑)
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




    print("""# CHECK - if "time" < 0 it must be -88""")
    # CHECK - if "time" < 0 it must be -88 (🛑 ERROR 🛑)
    # END OF CHECK - if "time" < 0 it must be -88 (🛑 ERROR 🛑)
    print("""# END OF CHECK - if "time" < 0 it must be -88""")


    print("""# CHECK - "time" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes""")
    # CHECK - "time" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    # END OF CHECK - "time" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    print("""# END OF CHECK - "time" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes""")


    print("""# CHECK - Magnification should be between 1 and 1000""")
    # CHECK - Magnification should be between 1 and 1000 (🟡 WARNING 🟡)
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

    # END OF CHECK - SpectralRange should have a format of "NUMBER-NUMBER" (Use regular expressions) 
    #       (For example, a good value in this column should look something like "185-3400")
    # (🛑 ERROR 🛑)
    print("""# END OF CHECK - SpectralRange should have a format of 'NUMBER-NUMBER' """)


    print("""# CHECK - SpectralRange min value should not be less than 0""")
    # CHECK - SpectralRange min value should not be less than 0 (🛑 ERROR 🛑)
    # END OF CHECK - SpectralRange min value should not be less than 0 (🛑 ERROR 🛑)
    print("""# END OF CHECK - SpectralRange min value should not be less than 0""")


    print("""# CHECK - SpectralRange min value should not be less than 400""")
    # CHECK - SpectralRange min value should not be less than 400 (🟡 WARNING 🟡)
    # END OF CHECK - SpectralRange min value should not be less than 400 (🟡 WARNING 🟡)
    print("""# END OF CHECK - SpectralRange min value should not be less than 400""")


    print("""# CHECK - SpectralRange max value should not be over 4000""")
    # CHECK - SpectralRange max value should not be over 4000 (🟡 WARNING 🟡)
    # END OF CHECK - SpectralRange max value should not be over 4000 (🟡 WARNING 🟡)
    print("""# END OF CHECK - SpectralRange max value should not be over 4000""")


    print("""# CHECK - SpectralRange min value cannot be more than the max value""")
    # CHECK - SpectralRange min value cannot be more than the max value (🛑 ERROR 🛑)
    # END OF CHECK - SpectralRange min value cannot be more than the max value (🛑 ERROR 🛑)
    print("""# END OF CHECK - SpectralRange min value cannot be more than the max value""")


    print("""# CHECK - SpectralResolution should be from ___ to ___""")
    # CHECK - SpectralResolution should be from ___ to ___ (🟡 WARNING 🟡)
    # END OF CHECK - SpectralResolution should be from ___ to ___ (🟡 WARNING 🟡)
    print("""# END OF CHECK - SpectralResolution should be from ___ to ___""")


    print("""# CHECK - if "time" < 0 it must be -88 (🛑 ERROR 🛑)""")
    # CHECK - if "time" < 0 it must be -88 (🛑 ERROR 🛑)
    # END OF CHECK - if "time" < 0 it must be -88 (🛑 ERROR 🛑)
    print("""# END OF CHECK - if "time" < 0 it must be -88 (🛑 ERROR 🛑)""")


    print("""# CHECK - "time" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes""")
    # CHECK - "time" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    # END OF CHECK - "time" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    print("""# END OF CHECK - "time" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes""")


    print("""# CHECK - NumberScans should be between ___ and ___""")
    # CHECK - NumberScans should be between ___ and ___ (🟡 WARNING 🟡)
    # END OF CHECK - NumberScans should be between ___ and ___ (🟡 WARNING 🟡)
    print("""# END OF CHECK - NumberScans should be between ___ and ___""")




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





    print("""# CHECK - Range for LaserWaveLength is 500 to 800""")
    # CHECK - Range for LaserWaveLength is 500 to 800 (🟡 WARNING 🟡)
    # END OF CHECK - Range for LaserWaveLength is 500 to 800 (🟡 WARNING 🟡)
    print("""# END OF CHECK - Range for LaserWaveLength is 500 to 800""")


    print("""# CHECK - Range for LaserGrating is 200 to 4000""")
    # CHECK - Range for LaserGrating is 200 to 4000 (🟡 WARNING 🟡)
    # END OF CHECK - Range for LaserGrating is 200 to 4000 (🟡 WARNING 🟡)
    print("""# END OF CHECK - Range for LaserGrating is 200 to 4000""")


    print("""# CHECK - SpectralRange should have a format of 'NUMBER-NUMBER' (Use regular expressions) """)
    # CHECK - SpectralRange should have a format of "NUMBER-NUMBER" (Use regular expressions) 
    #       (For example, a good value in this column should look something like "185-3400") 
    # (🛑 ERROR 🛑)

    # END OF CHECK - SpectralRange should have a format of "NUMBER-NUMBER" (Use regular expressions) 
    #       (For example, a good value in this column should look something like "185-3400")
    # (🛑 ERROR 🛑)
    print("""# END OF CHECK - SpectralRange should have a format of 'NUMBER-NUMBER' """)


    print("""# CHECK - SpectralRange min value should not be less than 0""")
    # CHECK - SpectralRange min value should not be less than 0 (🛑 ERROR 🛑)
    # END OF CHECK - SpectralRange min value should not be less than 0 (🛑 ERROR 🛑)
    print("""# END OF CHECK - SpectralRange min value should not be less than 0""")


    print("""# CHECK - SpectralRange min value should not be less than 50""")
    # CHECK - SpectralRange min value should not be less than 50 (🟡 WARNING 🟡)
    # END OF CHECK - SpectralRange min value should not be less than 50 (🟡 WARNING 🟡)
    print("""# END OF CHECK - SpectralRange min value should not be less than 50""")


    print("""# CHECK - SpectralRange max value should not be over 4000""")
    # CHECK - SpectralRange max value should not be over 4000 (🟡 WARNING 🟡)
    # END OF CHECK - SpectralRange max value should not be over 4000 (🟡 WARNING 🟡)
    print("""# END OF CHECK - SpectralRange max value should not be over 4000""")


    print("""# CHECK - SpectralRange min value cannot be more than the max value""")
    # CHECK - SpectralRange min value cannot be more than the max value (🛑 ERROR 🛑)
    # END OF CHECK - SpectralRange min value cannot be more than the max value (🛑 ERROR 🛑)
    print("""# END OF CHECK - SpectralRange min value cannot be more than the max value""")


    print("""# CHECK - SpectralResolution should be from ___ to ___""")
    # CHECK - SpectralResolution should be from ___ to ___ (🟡 WARNING 🟡)
    # END OF CHECK - SpectralResolution should be from ___ to ___ (🟡 WARNING 🟡)
    print("""# END OF CHECK - SpectralResolution should be from ___ to ___""")


    print("""# CHECK - Aperture should have a format of "NUMBER-NUMBER" (Use regular expressions) """)
    # CHECK - Aperture should have a format of "NUMBER-NUMBER" (Use regular expressions) 
    #       (For example, a good value in this column should look something like "100-150")
    # (🛑 ERROR 🛑)

    # END OF CHECK - Aperture should have a format of "NUMBER-NUMBER" (Use regular expressions) 
    #       (For example, a good value in this column should look something like "100-150")
    # (🛑 ERROR 🛑)
    print("""# END OF CHECK - Aperture should have a format of "NUMBER-NUMBER" (Use regular expressions) """)



    print("""# CHECK - Aperture minimum value cannot be more than the max value""")
    # CHECK - Aperture minimum value cannot be more than the max value (🛑 ERROR 🛑)
    # END OF CHECK - Aperture minimum value cannot be more than the max value (🛑 ERROR 🛑)
    print("""# END OF CHECK - Aperture minimum value cannot be more than the max value""")


    print("""# CHECK - Aperture minimum value cannot be less than 0""")
    # CHECK - Aperture minimum value cannot be less than 0 (🛑 ERROR 🛑)
    # END OF CHECK - Aperture minimum value cannot be less than 0 (🛑 ERROR 🛑)
    print("""# END OF CHECK - Aperture minimum value cannot be less than 0""")


    print("""# CHECK - Objective should be an integer 1 to 100""")
    # CHECK - Objective should be an integer 1 to 100 (🟡 WARNING 🟡)
    # END OF CHECK - Objective should be an integer 1 to 100 (🟡 WARNING 🟡)
    print("""# END OF CHECK - Objective should be an integer 1 to 100""")


    print("""# CHECK - MatchThreshold should be a number from 0 to 100 since it is a percentage""")
    # CHECK - MatchThreshold should be a number from 0 to 100 since it is a percentage (🛑 ERROR 🛑)
    # END OF CHECK - MatchThreshold should be a number from 0 to 100 since it is a percentage (🛑 ERROR 🛑)
    print("""# END OF CHECK - MatchThreshold should be a number from 0 to 100 since it is a percentage""")


    print("""# CHECK - if "time" < 0 it must be -88""")
    # CHECK - if "time" < 0 it must be -88 (🛑 ERROR 🛑)
    # END OF CHECK - if "time" < 0 it must be -88 (🛑 ERROR 🛑)
    print("""# END OF CHECK - if "time" < 0 it must be -88""")


    print("""# CHECK - "time" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes""")
    # CHECK - "time" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    # END OF CHECK - "time" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes (🟡 WARNING 🟡)
    print("""# END OF CHECK - "time" must be measured in hours - issue warning if it is over 15, telling them they should not report in minutes""")






    ##################################################################################################################################################
    # ---------------------------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------------- END OF RamanSettings Tab Checks ------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------------------------------------- #
    ##################################################################################################################################################




    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #

    

    # End of Microplastics Custom Checks
    print("# --- End of Microplastics Custom Checks --- #")



    return {'errors': errs, 'warnings': warnings}
    



