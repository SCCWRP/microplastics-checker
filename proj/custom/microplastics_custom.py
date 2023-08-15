# Dont touch this file! This is intended to be a template for implementing new custom checks
from inspect import currentframe
from flask import current_app, g
from .functions import checkData
import pandas as pd

def microplastics(all_dfs):
    
    current_function_name = str(currentframe().f_code.co_name)
    
    # function should be named after the dataset in app.datasets in __init__.py
    assert current_function_name in current_app.datasets.keys(), \
        f"function {current_function_name} not found in current_app.datasets.keys() - naming convention not followed"

    expectedtables = set(current_app.datasets.get(current_function_name).get('tables'))
    assert expectedtables.issubset(set(all_dfs.keys())), \
        f"""In function {current_function_name} - {expectedtables - set(all_dfs.keys())} not found in keys of all_dfs ({','.join(all_dfs.keys())})"""

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

    


    return {'errors': errs, 'warnings': warnings}
    



