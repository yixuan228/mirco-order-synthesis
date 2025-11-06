#!/usr/bin/env python
# coding: utf-8

import pandas as pd

# Project configuration
import sys
from pathlib import Path

CURR_PATH   = Path.cwd()
REPO_PATH   = CURR_PATH.parent
SCR_PATH    = REPO_PATH / 'scripts'

DATA_PATH       = REPO_PATH / 'data'
DATA_21_PATH    = REPO_PATH / 'data' / '2021-census-data'
DATA_GIS_PATH   = REPO_PATH / "data" / 'gis-files'          # path for all gis files

RESULTS_PATH    = REPO_PATH / "data" / 'results'            # path for all generated results
RES_STATIC      = RESULTS_PATH / 'static'                           # path for all intermediate results

sys.path.append(str(SCR_PATH))

# Coding scheme for inner London Boroughs
# Two coding scheme are adopted: 
# 1) E090xxx, Local Authority District, used in GIS files and consistent with Census Statistics Summary; 
# 2) E680xxx, Office for National Statistics(ONS), used in Census Safeguarded Data .

# London Borough, LB
LB_code = pd.read_csv(RES_STATIC / 'Coding_Scheme_Borough.csv')
LB_CODE_DICT_CENSUS = dict(zip(LB_code['Borough_Name'], LB_code['E680_Code_Census']))
LB_CODE_DICT_GIS = dict(zip(LB_code['Borough_Name'], LB_code['E090_Code_GIS']))

# Inner London Area, ILA
ILA_coding = pd.read_csv(RES_STATIC / 'Coding_Scheme_LMSOA_LAD.csv')
ILA_LSOA_CODE = ILA_coding['LSOA_CODE'].unique()
ILA_MSOA_CODE = ILA_coding['MSOA_CODE'].unique()
ILA_LAD_CODE = ILA_coding['LAD_CODE'].unique()
ILA_LAD_NAME = ILA_coding['LAD_NAME'].unique()

ILA_OA_CODE = ILA_coding['LSOA_CODE'].unique()  # Temporary

# Naming scheme: marginal-variable-distribution-geographical level
# geographical level:
# London Borough (lb) or Local Authority District (lad)
# Middle Super Output Area (msoa)       # Lower Super Output Area (lsoa)

# Get marginal distribution_age
def marg_age_dist(space_level='MSOA'):
    """Return Marginal Distribution of Age Attribute in designated space level: LAD, MSOA, LSOA, OA"""
    code_dict_map = {"LAD": ILA_LAD_CODE, "MSOA": ILA_MSOA_CODE, "LSOA": ILA_LSOA_CODE, "OA": ILA_OA_CODE}
    ILA_CODE = code_dict_map[space_level]

    if space_level == 'LAD': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS007-Age-By-Single-Year-2021-ltla-ONS.csv"
        var_col_name = 'Lower tier local authorities Code'
    if space_level == 'MSOA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS007-Age-By-Single-Year-2021-msoa-ONS.csv"
        var_col_name = 'Middle layer Super Output Areas Code'
    if space_level == 'LSOA': 
        print('Error: For Age attribute, there is no LSOA level statistics!')
        return 
    if space_level == 'OA': 
        print('Error: For Age attribute, there is no OA level statistics!')
        return 
    
    marg_var_all = pd.read_csv(var_stat_file)

    # long-wide form conversion
    marg_var_inner_london = marg_var_all[marg_var_all[var_col_name].isin(ILA_CODE)]
    marg_var_wide = marg_var_inner_london.pivot(index=var_col_name, columns='Age (101 categories) Code', values='Observation')

    marg_var_wide["0-15"] = marg_var_wide[list(range(0, 16))].sum(axis="columns")
    marg_var_wide["16-29"] = marg_var_wide[list(range(16, 30))].sum(axis="columns")
    marg_var_wide["30-49"] = marg_var_wide[list(range(30, 50))].sum(axis="columns")
    age_cols_50_plus = [col for col in marg_var_wide.columns if isinstance(col, int) and col >= 50]
    marg_var_wide["50+"] = marg_var_wide[age_cols_50_plus].sum(axis="columns")
    marg_var_summary = marg_var_wide[["0-15", "16-29", "30-49", "50+"]].copy()

    # add summary row
    var_sum_row = marg_var_summary.sum(axis=0)
    marg_var_summary = pd.concat([marg_var_summary, pd.DataFrame([var_sum_row], index=["TOTAL"])])

    marg_var_summary = marg_var_summary.div(marg_var_summary.sum(axis=1), axis=0)
    marg_var_summary.rename(columns={"0-15": 0, "16-29": 1, "30-49":2, "50+": 3}, inplace=True)
    
    # rename the index and columns
    marg_var_summary.index.name = 'GEO_CODE'
    marg_var_summary.columns.name = None
    
    return marg_var_summary

# marg_age_dist(space_level='OA')   # Usage


# Get marginal distribution_sex
def marg_sex_dist(space_level='MSOA'):
    """Return Marginal Distribution of Sex Attribute in designated space level: LAD, MSOA, LSOA, OA"""
    code_dict_map = {"LAD": ILA_LAD_CODE, "MSOA": ILA_MSOA_CODE, "LSOA": ILA_LSOA_CODE, "OA": ILA_OA_CODE}
    ILA_CODE = code_dict_map[space_level]

    if space_level == 'LAD': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS008-Sex-2021-ltla-ONS.csv"
        var_col_name = 'Lower tier local authorities Code'
    if space_level == 'MSOA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS008-Sex-2021-msoa-ONS.csv"
        var_col_name = 'Middle layer Super Output Areas Code'
    if space_level == 'LSOA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS008-Sex-2021-lsoa-ONS.csv"
        var_col_name = 'Lower layer Super Output Areas Code'
    if space_level == 'OA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS008-Sex-2021-oa-ONS.csv"
        var_col_name = 'Output Areas Code'
    
    marg_var_all = pd.read_csv(var_stat_file)

    # long-wide form conversion
    marg_var_inner_london = marg_var_all[marg_var_all[var_col_name].isin(ILA_CODE)]
    marg_var_wide = marg_var_inner_london.pivot(index=var_col_name, columns='Sex (2 categories) Code', values='Observation')

    # add summary row
    var_sum_row = marg_var_wide.sum(axis=0)
    marg_var_summary = pd.concat([marg_var_wide, pd.DataFrame([var_sum_row], index=["TOTAL"])])

    marg_var_summary = marg_var_summary.div(marg_var_summary.sum(axis=1), axis=0)
    marg_var_summary.rename(columns={1: 0, 2: 1}, inplace=True)

    # rename the index and columns
    marg_var_summary.index.name = 'GEO_CODE'
    marg_var_summary.columns.name = None

    return marg_var_summary

# marg_sex_dist(space_level='LAD')


# Get marginal distribution_ethnic
def marg_ethnic_dist(space_level='MSOA'):
    """Return Marginal Distribution of Ethnic Group Attribute in designated space level: LAD, MSOA, LSOA, OA"""
    code_dict_map = {"LAD": ILA_LAD_CODE, "MSOA": ILA_MSOA_CODE, "LSOA": ILA_LSOA_CODE, "OA": ILA_OA_CODE}
    ILA_CODE = code_dict_map[space_level]

    if space_level == 'LAD': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS021-Ethnic-Group-2021-ltla-ONS.csv"
        var_col_name = 'Lower tier local authorities Code'
    if space_level == 'MSOA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS021-Ethnic-Group-2021-msoa-ONS.csv"
        var_col_name = 'Middle layer Super Output Areas Code'
    if space_level == 'LSOA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS021-Ethnic-Group-2021-lsoa-ONS.csv"
        var_col_name = 'Lower layer Super Output Areas Code'
    if space_level == 'OA': 
        print('Error: For Ethnic Group attribute, there is no OA level statistics!')
        return 
    
    marg_var_all = pd.read_csv(var_stat_file)

    # long-wide form conversion
    marg_var_inner_london = marg_var_all[marg_var_all[var_col_name].isin(ILA_CODE)]
    marg_var_wide = marg_var_inner_london.pivot(index=var_col_name, columns='Ethnic group (20 categories)', values='Observation')

    # add summary row
    marg_var_wide['Asian'] = marg_var_wide[marg_var_wide.columns[[x.startswith("Asian") for x in marg_var_wide.columns]]].sum(axis='columns')
    marg_var_wide['Black'] = marg_var_wide[marg_var_wide.columns[[x.startswith("Black") for x in marg_var_wide.columns]]].sum(axis='columns')
    marg_var_wide['Mixed'] = marg_var_wide[marg_var_wide.columns[[x.startswith("Mixed") for x in marg_var_wide.columns]]].sum(axis='columns')
    marg_var_wide['White'] = marg_var_wide[marg_var_wide.columns[[x.startswith("White") for x in marg_var_wide.columns]]].sum(axis='columns')
    marg_var_wide['Other'] = marg_var_wide[marg_var_wide.columns[[x.startswith("Other") for x in marg_var_wide.columns]]].sum(axis='columns')

    marg_var_wide = marg_var_wide[["Asian", "Black", "Mixed", "White", "Other"]]

    var_sum_row = marg_var_wide.sum(axis=0)
    marg_var_summary = pd.concat([marg_var_wide, pd.DataFrame([var_sum_row], index=["TOTAL"])])

    marg_var_summary = marg_var_summary.div(marg_var_summary.sum(axis=1), axis=0)
    marg_var_summary.rename(columns={"Asian":0, "Black":1, "Mixed":2, "White":3, "Other":4}, inplace=True)

    # rename the index and columns
    marg_var_summary.index.name = 'GEO_CODE'
    marg_var_summary.columns.name = None
    
    return marg_var_summary

# marg_ethnic_dist(space_level='MSOA')


# Get marginal distribution_economic activity
def marg_ecoact_dist(space_level='MSOA'):
    """Return Marginal Distribution of Economic Activity Status Attribute in designated space level: LAD, MSOA, LSOA, OA"""
    code_dict_map = {"LAD": ILA_LAD_CODE, "MSOA": ILA_MSOA_CODE, "LSOA": ILA_LSOA_CODE, "OA": ILA_OA_CODE}
    ILA_CODE = code_dict_map[space_level]

    if space_level == 'LAD': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS066-Economic-Activity-Status-2021-ltla-ONS.csv"
        var_col_name = 'Lower tier local authorities Code'
    if space_level == 'MSOA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS066-Economic-Activity-Status-2021-msoa-ONS.csv"
        var_col_name = 'Middle layer Super Output Areas Code'
    if space_level == 'LSOA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS066-Economic-Activity-Status-2021-lsoa-ONS.csv"
        var_col_name = 'Lower layer Super Output Areas Code'
    if space_level == 'OA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS066-Economic-Activity-Status-2021-oa-ONS.csv"
        var_col_name = 'Output Areas Code'

    marg_var_all = pd.read_csv(var_stat_file)

    # long-wide form conversion
    marg_var_inner_london = marg_var_all[marg_var_all[var_col_name].isin(ILA_CODE)]
    marg_var_wide = marg_var_inner_london.pivot(index=var_col_name, columns='Economic activity status (20 categories) Code', values='Observation')

    marg_var_wide['Employed'] = marg_var_wide[[1, 2, 3, 4, 5, 6, 8]].sum(axis='columns')
    marg_var_wide['Unemployed'] = marg_var_wide[[7, 9]].sum(axis='columns')
    marg_var_wide['Inactive'] = marg_var_wide[[10, 11, 12, 13, 14]].sum(axis='columns')
    marg_var_wide = marg_var_wide[['Employed', 'Unemployed', 'Inactive']]

    # add summary row
    var_sum_row = marg_var_wide.sum(axis=0)
    marg_var_summary = pd.concat([marg_var_wide, pd.DataFrame([var_sum_row], index=["TOTAL"])])

    marg_var_summary = marg_var_summary.div(marg_var_summary.sum(axis=1), axis=0)
    marg_var_summary.rename(columns={"Employed":0, "Unemployed":1, "Inactive":2}, inplace=True)

    # rename the index and columns
    marg_var_summary.index.name = 'GEO_CODE'
    marg_var_summary.columns.name = None

    return marg_var_summary

# marg_ecoact_dist(space_level='LAD')


# Get marginal distribution_car_numbers
def marg_car_dist(space_level='MSOA'):
    """Return Marginal Distribution of Car/Van Availability Attribute in designated space level: LAD, MSOA, LSOA, OA"""
    code_dict_map = {"LAD": ILA_LAD_CODE, "MSOA": ILA_MSOA_CODE, "LSOA": ILA_LSOA_CODE, "OA": ILA_OA_CODE}
    ILA_CODE = code_dict_map[space_level]

    if space_level == 'LAD': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS045-Car-Or-Van-Availability-2021-ltla-ONS.csv"
        var_col_name = 'Lower tier local authorities Code'
    if space_level == 'MSOA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS045-Car-Or-Van-Availability-2021-msoa-ONS.csv"
        var_col_name = 'Middle layer Super Output Areas Code'
    if space_level == 'LSOA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS045-Car-Or-Van-Availability-2021-lsoa-ONS.csv"
        var_col_name = 'Lower layer Super Output Areas Code'
    if space_level == 'OA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS045-Car-Or-Van-Availability-2021-oa-ONS.csv"
        var_col_name = 'Output Areas Code'

    marg_var_all = pd.read_csv(var_stat_file)

    # long-wide form conversion
    marg_var_inner_london = marg_var_all[marg_var_all[var_col_name].isin(ILA_CODE)]
    marg_var_wide = marg_var_inner_london.pivot(index=var_col_name, columns='Car or van availability (5 categories) Code', values='Observation')

    # add summary row
    var_sum_row = marg_var_wide.sum(axis=0)
    marg_var_summary = pd.concat([marg_var_wide, pd.DataFrame([var_sum_row], index=["TOTAL"])]).drop(columns=[-8])
    marg_var_summary = marg_var_summary.div(marg_var_summary.sum(axis=1), axis=0)

    # rename the index and columns
    marg_var_summary.index.name = 'GEO_CODE'
    marg_var_summary.columns.name = None
    
    return marg_var_summary

# marg_car_dist(space_level='LAD')


# Get marginal distribution_legal partnership
def marg_leptnershp_dist(space_level='MSOA'):
    """Return Marginal Distribution of Legal Partnership Status in designated space level: LAD, MSOA, LSOA, OA"""
    code_dict_map = {"LAD": ILA_LAD_CODE, "MSOA": ILA_MSOA_CODE, "LSOA": ILA_LSOA_CODE, "OA": ILA_OA_CODE}
    ILA_CODE = code_dict_map[space_level]

    if space_level == 'LAD': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS002-Legal-Partnership-Status-2021-ltla-ONS.csv"
        var_col_name = 'Lower tier local authorities Code'
    if space_level == 'MSOA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS002-Legal-Partnership-Status-2021-msoa-ONS.csv"
        var_col_name = 'Middle layer Super Output Areas Code'
    if space_level == 'LSOA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS002-Legal-Partnership-Status-2021-lsoa-ONS.csv"
        var_col_name = 'Lower layer Super Output Areas Code'
    if space_level == 'OA': 
        print('Error: For Legal Partnership Status attribute, there is no OA level statistics!')
        return 

    marg_var_all = pd.read_csv(var_stat_file)

    # long-wide form conversion
    marg_var_inner_london = marg_var_all[marg_var_all[var_col_name].isin(ILA_CODE)]
    marg_var_wide = marg_var_inner_london.pivot(index=var_col_name, columns='Marital and civil partnership status (12 categories) Code', values='Observation')
    
    marg_var_wide['Single'] = marg_var_wide[[1, ]].sum(axis='columns')
    marg_var_wide['Married/Registered Same-sex'] = marg_var_wide[[2, 3, 4, 5]].sum(axis='columns')
    marg_var_wide['Separated/Divorced/Widowed'] = marg_var_wide[[6, 7, 8, 9, 10, 11]].sum(axis='columns')
    marg_var_wide = marg_var_wide[['Single', 'Married/Registered Same-sex', 'Separated/Divorced/Widowed']]

    # add summary row
    var_sum_row = marg_var_wide.sum(axis=0)
    marg_var_summary = pd.concat([marg_var_wide, pd.DataFrame([var_sum_row], index=["TOTAL"])])
    
    marg_var_summary = marg_var_summary.div(marg_var_summary.sum(axis=1), axis=0)
    marg_var_summary.rename(columns = {'Single':0, 'Married/Registered Same-sex':1, 'Separated/Divorced/Widowed':2}, inplace=True)

    # rename the index and columns
    marg_var_summary.index.name = 'GEO_CODE'
    marg_var_summary.columns.name = None
    
    return marg_var_summary

# marg_leptnershp_dist(space_level='LAD')

# Get Population Distribution of different areas
def pop_dist(space_level='MSOA'):
    """Return Distribution of Population in designated space level: LAD, MSOA, LSOA, OA"""
    code_dict_map = {"LAD": ILA_LAD_CODE, "MSOA": ILA_MSOA_CODE, "LSOA": ILA_LSOA_CODE, "OA": ILA_OA_CODE}
    ILA_CODE = code_dict_map[space_level]

    if space_level == 'LAD': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS001-Number-Of-Usual-Residents-In-Households-And-Communal-Establishments-2021-ltla-ONS.csv"
        var_col_name = 'Lower tier local authorities Code'
    if space_level == 'MSOA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS001-Number-Of-Usual-Residents-In-Households-And-Communal-Establishments-2021-msoa-ONS.csv"
        var_col_name = 'Middle layer Super Output Areas Code'
    if space_level == 'LSOA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS001-Number-Of-Usual-Residents-In-Households-And-Communal-Establishments-2021-lsoa-ONS.csv"
        var_col_name = 'Lower layer Super Output Areas Code'
    if space_level == 'OA': 
        var_stat_file = DATA_21_PATH / "statistic-summary" / space_level / "TS001-Number-Of-Usual-Residents-In-Households-And-Communal-Establishments-2021-oa-ONS.csv"
        var_col_name = 'Output Areas Code'
    
    marg_var_all = pd.read_csv(var_stat_file)
    marg_var_inner_london = marg_var_all[marg_var_all[var_col_name].isin(ILA_CODE)]

    pop_sum = marg_var_inner_london.groupby(var_col_name)['Observation'].sum()
    pop_percent = pop_sum / pop_sum.sum()

    marg_var_summary = pd.DataFrame({'Total': pop_sum,'Percent': pop_percent})
    marg_var_summary.index.name = None

    marg_var_summary.to_csv(DATA_21_PATH / 'statistic-summary' / f'population_distribution_{space_level}.csv')
    print(f'Data Saved as csv file, in {space_level} Level')
    
    return marg_var_summary

# pop_dist(space_level='MSOA')