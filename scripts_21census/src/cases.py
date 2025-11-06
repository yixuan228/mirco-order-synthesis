from src.basics import Demographics, Constraints, Population
import random
from itertools import product
from pathlib import Path
import pandas as pd
import numpy as np


# Project configuration
from pathlib import Path

CURR_PATH       = Path(__file__).resolve().parent           # current file path (under src path)
SCRIPT_PATH     = CURR_PATH.parent                          # folder scripts_21census
REPO_PATH       = SCRIPT_PATH.parent                        # current repository path
DATA_PATH       = REPO_PATH / "data"                        # path for saving the data
DATA_21_PATH    = REPO_PATH / 'data' / '2021-census-data'   # path for all census data related files
SRC_PATH        = REPO_PATH / "scripts_21census" / 'src'


VAR_RENAME_CENSUS_2021 = {
    "resident_id_m":                "resident_id",
    "approx_social_grade":          "approximated_social_grade",
    "economic_activity_status_15m": "economic_activity",
    "employment_status":            "employment_status",
    "english_proficiency_5a":       "english_proficiency",
    "ethnic_group_tb_20b":          "ethnic_group",
    "gltla22cd":                    "borough_code",
    "hh_size_7a":                   "household_size",
    "highest_qualification":        "highest_qualification",
    "legal_partnership_status_7a":  "marital_status",
    "number_of_cars_6a":            "number_of_cars_and_vans",
    "resident_age_18m":             "age",
    "sex":                          "sex",
}

VAR_CODE_CENSUS_2021_INIT = {
    "approximated_social_grade": {1: "AB", 2: "C1", 3: "C2", 4: "DE"},

    "economic_activity": {
        1: "Employed (non-student): Employee, Part-time",
        2: "Employed (non-student): Employee, Full-time",
        3: "Employed (non-student): Self-employed with employees, Part-time",
        4: "Employed (non-student): Self-employed with employees, Full-time",
        5: "Employed (non-student): Self-employed without employees, Part-time",
        6: "Employed (non-student): Self-employed without employees, Full-time",
        7: "Unemployed (non-student): Seeking work, available within 2 weeks",
        8: "Employed full-time student",
        9: "Unemployed full-time student: Seeking work, available within 2 weeks",
        10: "Economically inactive: Retired",
        11: "Economically inactive: Student",
        12: "Economically inactive: Looking after home/family",
        13: "Economically inactive: Long-term sick or disabled",
        14: "Economically inactive: Other",},

    "employment_status": {
        # -8: "Code not required",
        1: "Employee",
        2: "Self-employed or freelance (no employees)",
        3: "Self-employed with employees",},

    "english_proficiency": {
        # -8: "Does not apply",
        1: "Main language is English",
        2: "Non-English: Speaks very well or well",
        3: "Non-English: Cannot speak well",
        4: "Non-English: Cannot speak at all",},

    "ethnic_group": {
        # -8: "Does not apply",
        1: "Asian: Bangladeshi", 2: "Asian: Chinese", 3: "Asian: Indian", 
        4: "Asian: Pakistani", 5: "Asian: Other Asian", 6: "Black: African",
        7: "Black: Caribbean", 8: "Black: Other Black", 9: "Mixed: White and Asian",
        10: "Mixed: White and Black African", 11: "Mixed: White and Black Caribbean",
        12: "Mixed: Other Mixed", 13: "White: British (Eng/Wal/Sco/N.I.)",
        14: "White: Irish", 15: "White: Gypsy or Irish Traveller", 
        16: "White: Roma", 17: "White: Other White", 18: "Other: Arab", 
        19: "Other: Any other ethnic group",}, 

    "borough_code":{
        "E68000208": "Westminster", # including City of London
        "E68000214": "Camden",
        "E68000218": "Greenwich",
        "E68000219": "Hackney",
        "E68000220": "Hammersmith and Fulham",
        "E68000226": "Islington",
        "E68000227": "Kensington and Chelsea",
        "E68000229": "Lambeth",
        "E68000230": "Lewisham",
        "E68000235": "Southwark",
        "E68000237": "Tower Hamlets",
        "E68000239": "Wandsworth",
        "E68000232": "Newham",},

    "household_size": {0: "0 person in household",  1: "1 person in household",
                       2: "2 persons in household", 3: "3 persons in household",
                       4: "4 persons in household", 5: "5 persons in household",
                       6: "6 or more people in household",},

    "highest_qualification": {
        # -8: "Does not apply",
        0: "No qualifications",
        1: "Level 1: 1–4 GCSEs or equivalent",
        2: "Level 2: 5+ GCSEs or equivalent",
        3: "Apprenticeship",
        4: "Level 3: 2+ A-levels or equivalent",
        5: "Level 4+: Degree or higher (BA, MA, PhD)",
        6: "Other vocational/work-related qualifications",},

    "marital_status": {1: "Single", 2: "Married", 3: "Registered civil partnership",
                       4: "Separated", 5: "Divorced", 6: "Widowed"},

    "number_of_cars_and_vans": {0: "No car/van", 1: "1 car/van", 2: "2 cars/vans",
                                3: "3 cars/vans", 4: "4 or more cars/vans"},

    "age": {1: "Aged 4 years and under",    2: "Aged 5 to 9 years", 
            3: "Aged 10 to 15 years",       4: "Aged 16 to 18 years",
            5: "Aged 19 to 24 years",       6: "Aged 25 to 29 years",
            7: "Aged 30 to 34 years",       8: "Aged 35 to 39 years",
            9: "Aged 40 to 44 years",       10: "Aged 45 to 49 years",
            11: "Aged 50 to 54 years",      12: "Aged 55 to 59 years", 
            13: "Aged 60 to 64 years",      14: "Aged 65 to 69 years",
            15: "Aged 70 to 74 years",      16: "Aged 75 to 79 years",
            17: "Aged 80 to 84 years",      18: "Aged 85 years and over",},

    "sex": {1: "Female", 2: "Male"},
  
}

VAR_CODE_CENSUS_2021_SIMPLIFIED = {
    "age": {0: "0-15", 1: "16-29", 2: "30-49", 3: "50+"},
    "sex": {0: "Female", 1: "Male"},
    "marital_status": {0: "Single",
                       1: "Married/Registered Same-sex",
                       2: "Separated/Divorced/Widowed"},
                       
    "economic_activity": {0:"Employed", 1: "Unemployed", 2: "Inactive"}, 
    "ethnic_group": {0: "Asian", 1: "Black", 2: "Mixed", 3: "White", 4: "Other"},
    "number_of_cars_and_vans": {0: "No car/van", 1: "1 car/van", 2: "2 cars/vans",
                                3: "3 or more cars/vans",},
    "approximated_social_grade": {0: "AB", 1: "C1", 2: "C2", 3: "DE"},

}

VAR_RECODE_MAP_CENSUS_2021_INIT2SIMPLIFIED = {
    "age": {0: [1,2,3], 
            1: [4,5,6],
            2: [7,8,9,10], 
            3: [11,12,13,14,15,16,17,18]},
    "sex": {0: [1, ], 1: [2, ]},
    "marital_status": {0: [1, ], 1: [2, 3], 2: [4, 5, 6]},
    "economic_activity": {0: [1, 2, 3, 4, 5, 6, 8],
                 1: [7, 9],
                 2: [10, 11, 12, 13, 14]},
    "ethnic_group": {0: [1,2,3,4,5], 
                     1: [6,7,8],
                     2: [9,10,11,12],
                     3: [13,14,15,16,17], 4: [18,19]},
    "number_of_cars_and_vans": {0: [0, ], 1: [1, ], 2: [2, ], 3:[3, 4]},
    "approximated_social_grade": {0: [1, ], 1: [2, ], 2: [3, ], 3: [4, ]},
}

def fillna_column(file, column, na_value, random_seed=100):
    """Fill missing values in a column based on the distribution of existing values."""
    if random_seed is not None:
        np.random.seed(random_seed)    # make sure reproducibility

    df_existing = file[file[column] != na_value]
    dist = df_existing[column].value_counts(normalize=True)
    file.loc[file[column]==na_value,column] = np.random.choice(dist.index, 
                                           size=len(file)-len(df_existing),
                                           p=dist.values)
    return file


def get_census_2021_base_population(microdata_path: Path = DATA_21_PATH / 'census_microdata_2021_inner_london.csv', simplified=True) -> Population:
    """Get base population from census 2021 microdata(csv file): load, rename variables, fill missing and simplify categories.""" 

    census_records = pd.read_csv(microdata_path)
    census_records = census_records.reindex(columns=list(VAR_CODE_CENSUS_2021_INIT.keys()))

    # fill the missing values based on the value distribution
    columns_to_fill = ["approximated_social_grade", "economic_activity", "english_proficiency", "ethnic_group","employment_status", # employment_status over 25% missing
                    "highest_qualification", "marital_status", "number_of_cars_and_vans", ]
    na_value = -8
    for col in columns_to_fill:
        census_records = fillna_column(census_records, col, na_value)

    census_demographics = Demographics(VAR_CODE_CENSUS_2021_INIT)
    population = Population(census_demographics, census_records)

    # simplify categories
    if simplified:
        population.recode_variable(new_var_code_cate=VAR_CODE_CENSUS_2021_SIMPLIFIED,
                                var_recode_map=VAR_RECODE_MAP_CENSUS_2021_INIT2SIMPLIFIED)
        
    return population

from tqdm import tqdm

def get_synthetic_population(syn_pop_path:Path = DATA_PATH / 'results' / 'static'/ 'synthetic_population_LSOA_level.csv', If_ILA=True, area_codes=None):
    """"
    Load synthetic population from CSV and return a dictionary of Population objects.

    Parameters:
        syn_pop_path (Path): Path to the synthetic population CSV file.
        If_ILA (bool): If True, load the entire population for all area codes. If False, load only selected area_codes.
        area_codes (list or None): List of area codes to load if If_ILA is False. Must be provided in that case.

    Returns:
        dict: A dictionary where keys are area codes and values are Population objects.
    
    Raises:
        ValueError: If If_ILA is False but no area_codes are provided.
    """
    
    syn_pop_all = pd.read_csv(syn_pop_path)
    syn_pop_var_list = [col for col in syn_pop_all.columns if col != 'weights' and col != 'area_code']
    syn_var_cate_dict = {k:VAR_CODE_CENSUS_2021_SIMPLIFIED[k] for k in syn_pop_var_list}

    syn_pop_dict = {}   # save the syn pop results
    if If_ILA:          # load all synthetic population results
        area_codes = syn_pop_all['area_code'].unique()
        
        for code in tqdm(area_codes, desc='Loading Synthetic Population'):
            pop_df = syn_pop_all[syn_pop_all['area_code'] == code]

            records =  pop_df.drop(columns=['area_code', 'weights'])
            syn_pop_area = Population(demographics=Demographics(syn_var_cate_dict), records=records, weights=pop_df['weights'])

            syn_pop_dict[code] = syn_pop_area
    else:
        if not area_codes:
            raise ValueError('No area code is provided!')
        for code in tqdm(area_codes, desc='Loading Synthetic Population'):
            pop_df = syn_pop_all[syn_pop_all['area_code'] == code]

            records =  pop_df.drop(columns=['area_code', 'weights'])
            syn_pop_area = Population(demographics=Demographics(syn_var_cate_dict), records=records, weights=pop_df['weights'])

            syn_pop_dict[code] = syn_pop_area

    return syn_pop_dict