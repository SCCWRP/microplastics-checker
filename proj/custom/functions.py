import json, os
from pandas import isnull, DataFrame, to_datetime, read_sql
import math
import numpy as np
from inspect import currentframe
import pandas as pd
from flask import current_app
import json

def checkData(tablename, badrows, badcolumn, error_type, error_message = "Error", is_core_error = False, errors_list = [], q = None, **kwargs):
    
    # See comments on the get_badrows function
    # doesnt have to be used but it makes it more convenient to plug in a check
    # that function can be used to get the badrows argument that would be used in this function
    if len(badrows) > 0:
        if q is not None:
            # This is the case where we run with multiprocessing
            # q would be a mutliprocessing.Queue() 
            q.put({
                "table": tablename,
                "rows":badrows,
                "columns":badcolumn,
                "error_type":error_type,
                "is_core_error" : is_core_error,
                "error_message":error_message
            })

        return {
            "table": tablename,
            "rows":badrows,
            "columns":badcolumn,
            "error_type":error_type,
            "is_core_error" : is_core_error,
            "error_message":error_message
        }
    return {}


def mismatch(df1, df2, mergecols = None, left_mergecols = None, right_mergecols = None, row_identifier = 'tmp_row'):
    
    # gets rows in df1 that are not in df2
    # row identifier column is tmp_row by default

    if mergecols is not None:
        assert set(mergecols).issubset(set(df1.columns)), f"""In mismatch function - {','.join(mergecols)} is not a subset of the columns of the dataframe """
        assert set(mergecols).issubset(set(df2.columns)), f"""In mismatch function - {','.join(mergecols)} is not a subset of the columns of the dataframe """
        tmp = df1 \
            .merge(
                df2.assign(_present_='yes'),
                on = mergecols, 
                how = 'left',
                suffixes = ('','_df2')
            )
    
    elif (right_mergecols is not None) and (left_mergecols is not None):
        assert set(left_mergecols).issubset(set(df1.columns)), f"""In mismatch function - {','.join(left_mergecols)} is not a subset of the columns of the dataframe of the first argument"""
        assert set(right_mergecols).issubset(set(df2.columns)), f"""In mismatch function - {','.join(right_mergecols)} is not a subset of the columns of the dataframe of the second argument"""
        
        tmp = df1 \
            .merge(
                df2.assign(_present_='yes'),
                left_on = left_mergecols, 
                right_on = right_mergecols, 
                how = 'left',
                suffixes = ('','_df2')
            )

    else:
        raise Exception("In mismatch function - improper use of function - No merging columns are defined")

    if not tmp.empty:
        badrows = tmp[isnull(tmp._present_)][row_identifier].tolist() \
            if row_identifier not in (None, 'index') \
            else tmp[isnull(tmp._present_)].index.tolist()
    else:
        badrows = []

    return badrows



def check_time(starttime, endtime):
    df_over = to_datetime(starttime)
    df_start = to_datetime(endtime)
    times = (df_over - df_start).astype('timedelta64[m]')
    return abs(times)


def multivalue_lookup_check(df, field, listname, listfield, dbconnection, displayfieldname = None, sep=','):
    """
    Checks a column of a dataframe against a column in a lookup list. Specifically if the column may have multiple values.
    The default is that the user enters multiple values separated by a comma, although the function may take other characters as separators
    
    Parameters:
    df               : The user's dataframe
    field            : The field name of the user's submitted dataframe
    listname         : The Lookup list name (for example lu_resqualcode)
    listfield        : The field of the lookup list table that we are checking against
    displayfieldname : What the user will see in the error report - defaults to the field argument 
                       it should still be a column in the dataframe, but with different capitalization

    Returns a dictionary of arguments to pass to the checkData function
    """

    # default the displayfieldname to the "field" argument
    displayfieldname = displayfieldname if displayfieldname else field

    # displayfieldname should still be a column of the dataframe, but just typically camelcased
    assert displayfieldname.lower() in df.columns, f"the displayfieldname {displayfieldname} was not found in the columns of the dataframe, even when it was lowercased"

    assert field in df.columns, f"In {str(currentframe().f_code.co_name)} (value against multiple values check) - {field} not in the columns of the dataframe"
    lookupvals = set(read_sql(f'''SELECT DISTINCT "{listfield}" FROM "{listname}";''', dbconnection)[listfield].tolist())

    if not 'tmp_row' in df.columns:
        df['tmp_row'] = df.index

    # hard to explain what this is doing through a code comment
    badrows = df[df[field].apply(lambda values: not set([val.strip() for val in str(values).split(sep)]).issubset(lookupvals) )].tmp_row.tolist()
    args = {
        "badrows": badrows,
        "badcolumn": displayfieldname,
        "error_type": "Lookup Error",
        "error_message": f"""One of the values here is not in the lookup list <a target = "_blank" href=/{current_app.script_root}/scraper?action=help&layer={listname}>{listname}</a>"""
    }

    return args


# For benthic, we probably have to tack on a column that just contains values that say "Infauna" and then use that as the parameter column
# For chemistry, we have to tack on the analyteclass column from lu_analytes and then use that as the parameter column
def sample_assignment_check(eng, df, parameter_column, row_index_col = 'tmp_row', stationid_column = 'stationid', dataframe_agency_column = 'lab', assignment_agency_column = 'assigned_agency', assignment_table = 'vw_sample_assignment'):
    '''
        Simply Returns the "badrows" list of indices where the parameter and lab doesnt match the assignment table
    '''
    # No SQL injection
    assignment_table = str(assignment_table).replace(';','').replace('"','').replace("'","")
    stationid_column = str(stationid_column).replace(';','').replace('"','').replace("'","")
    dataframe_agency_column = str(dataframe_agency_column).replace(';','').replace('"','').replace("'","")
    assignment_agency_column = str(assignment_agency_column).replace(';','').replace('"','').replace("'","")
    parameter_column = str(parameter_column).replace(';','').replace('"','').replace("'","")
    
    assignment = pd.read_sql(
        f'''SELECT DISTINCT {stationid_column}, parameter AS {parameter_column}, {assignment_agency_column} AS {dataframe_agency_column}, 'yes' AS present FROM "{assignment_table}"; ''', 
        eng
    )

    df = df.merge(assignment, on = [stationid_column, parameter_column, dataframe_agency_column], how = 'left')


    badrows = df[(df.present.isnull()) & (df[stationid_column] != '0000')][row_index_col].tolist() if row_index_col != 'index' else df[(df.present.isnull() ) & (df[stationid_column] != '0000')].index.tolist()

    return badrows



# Check Logic of Grab/Trawl Numbers and only return the badrows
def check_samplenumber_sequence(df_to_check, col, samplenumbercol):
    assert col in df_to_check.columns, f"{col} not found in columns of the dataframe passed into check_samplenumber_sequence"
    assert 'stationid' in df_to_check.columns, "'stationid' not found in columns of the dataframe passed into check_samplenumber_sequence"
    assert 'sampledate' in df_to_check.columns, "'sampledate' not found in columns of the dataframe passed into check_samplenumber_sequence"

    df_to_check[col] = pd.to_datetime(df_to_check[col], format='%H:%M:%S').dt.time

    df_to_check = df_to_check.sort_values(['stationid', 'sampledate', col])

    trawl_grouped = df_to_check.groupby(['stationid', 'sampledate']).apply(lambda grp: grp[samplenumbercol].is_monotonic_increasing).reset_index()
    trawl_grouped.columns = ['stationid', 'sampledate', 'correct_order']

    badrows = df_to_check.merge(
            trawl_grouped[trawl_grouped['correct_order'] == False],
            on = ['stationid', 'sampledate'],
            how = 'inner'
        ) \
        .tmp_row \
        .tolist()
    return badrows