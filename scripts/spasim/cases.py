from spasim.basics import Demographics, Constraints, Population
import random
from itertools import product
import pandas as pd
import numpy as np

VAR_RENAME_CENSUS_2011 = {
    "age": "age",
    "sex": "sex",
    "sizhuk": "household_size",
    "langprf": "english_proficiency",
    "marstat": "marital_status",
    "carsnoc": "number_of_cars_and_vans",
    "ecopuk": "economic_activity",
    "ethnicityew": "ethnic_group",
    "hlqupuk11": "highest_qualification",
    "scgpuk11c": "approximated_social_grade"
}

VAR_CODE_CENSUS_2011_INIT = {
    "age": {code: str(code) for code in range(0, 91)},
    "sex": {1: "Male", 2: "Female"},
    "household_size": {0: "0 person in household", 1: "1 persons in household",
                       2: "2 persons in household", 3: "3 persons in household",
                       4: "4 persons in household", 5: "5 persons in household",
                       6: "6 persons in household", 7: "7 persons in household",
                       8: "8 persons in household", 9: "9 or more persons in household"},
    "marital_status": {1: "Single", 2: "Married", 3: "Registered Same-sex",
                       4: "Separated", 5: "Divorced", 6: "Widowed"},
    "ethnic_group": {1: "White-British", 2: "White-Irish", 3: "White-Gypsy",
                     4: "White-Other White", 5: "Mixed-Caribbean", 6: "Mixed-African",
                     7: "Mixed-Asian", 8: "Mixed-Other Mixed", 9: "Asian-Indian",
                     10: "Asian-Pakistani", 11: "Asian-Bangladeshi", 12: "Asian-Chinese",
                     13: "Asian-Other Asian", 14: "Black-African", 15: "Black-Caribbean",
                     16: "Black-Other Black", 17: "Other-Arab", 18: "Other-Any Other"},
    "approximated_social_grade": {1: "AB", 2: "C1", 3: "C2", 4: "DE"},
    "number_of_cars_and_vans": {0: "No car/van", 1: "1 car/van", 2: "2 cars/vans",
                                3: "3 cars/vans", 4: "4 or more cars/vans"}
}

VAR_CODE_CENSUS_2011_SIMPLIFIED = {
    "age": {0: "0-15", 1: "16-29", 2: "30-49", 3: "50+"},
    "sex": {0: "Male", 1: "Female"},
    "household_size": {0: "0 person in household", 1: "1 persons in household",
                       2: "2 persons in household", 3: "3 persons in household",
                       4: "4 persons in household", 5: "5 persons in household",
                       6: "6 or more persons in household"},
    "marital_status": {0: "Single",
                       1: "Married/Registered Same-sex",
                       2: "separated/divorced/widowed"},
    "ethnic_group": {0: "White", 1: "Mixed", 2: "Asian", 3: "Black", 4: "Other"},
    "approximated_social_grade": {0: "AB", 1: "C1", 2: "C2", 3: "DE"},
    "number_of_cars_and_vans": {0: "No car/van", 1: "1 car/van",
                                2: "2 cars/vans", 3: "3 cars/vans",
                                4: "4 or more cars/vans"}
}

VAR_RECODE_MAP_CENSUS_2011_INIT2SIMPLIFIED = {
    "age": {0: list(range(0, 16)), 1: list(range(16, 30)),
            2: list(range(30, 50)), 3: list(range(50, 91))},
    "sex": {0: [1, ], 1: [2, ]},
    "household_size": {0: [0, ], 1: [1, ], 2: [2, ], 3: [3, ],
                       4: [4, ], 5: [5, ], 6: [6, 7, 8, 9]},
    "marital_status": {0: [1, ], 1: [2, 3], 2: [4, 5, 6]},
    "ethnic_group": {0: [1, 2, 3, 4], 1: [5, 6, 7, 8],
                     2: [9, 10, 11, 12, 13],
                     3: [14, 15, 16], 4: [17, 18]},
    "approximated_social_grade": {0: [1, ], 1: [2, ], 2: [3, ], 3: [4, ]},
    "number_of_cars_and_vans": {0: [0, ], 1: [1, ], 2: [2, ],
                                3: [3, ], 4: [4, ]}
}

INNER_LONDON_BOROUGH_NAME = ["Camden", "Greenwich", "Hackney", "Hammersmith and Fulham",
                             "Islington", "Kensington and Chelsea", "Lambeth", "Lewisham",
                             "Southwark", "Tower Hamlets", "Wandsworth", "Westminster"]


def simple_random_case(var_cate_code=None, marg_dist=None, pop_size=10000, random_seed=100):
    # input - variable categorising/coding and marginal distribution
    if var_cate_code is None:
        var_cate_code = {
            "age": {0: "0-15", 1: "16-60", 2: "60+"},
            "sex": {0: "male", 1: "female"},
            "marital status": {0: "single", 1: "married", 2: "divorced", 3: "same-sex"}
        }
    if marg_dist is None:
        marg_dist = {
            "age": {0: 0.25, 1: 0.5, 2: 0.25},
            "sex": {0: 0.48, 1: 0.52},
            "marital status": {0: 0.47, 1: 0.37, 2: 0.07, 3: 0.09}
        }

    # initialize constraints
    constraints = Constraints(var_cate_code, marg_dist)  # constraints is a special demographics with

    # initialize random base population
    random.seed(random_seed)
    ind_cate_set = list(product(*[var_cate_code[var].keys() for var in var_cate_code]))
    records = random.choices(ind_cate_set, k=pop_size)
    base_pop = Population(demographics=constraints, records=records)

    return base_pop, constraints

def fillna_column(file,column,na_value):
    df_existing = file[file[column] != na_value]
    dist = df_existing[column].value_counts(normalize=True)
    file.loc[file[column]==na_value,column] = np.random.choice(dist.index, 
                                           size=len(file)-len(df_existing),
                                           p=dist.values)
    return file


def get_census_2011_base_population(microdata_file, simplified=True):
    """Get base population from census 2011 microdata"""

    census_records = pd.read_csv(microdata_file)

    census_records = census_records.reindex(columns=list(VAR_CODE_CENSUS_2011_INIT.keys()))
    census_records = fillna_column(census_records,"ethnic_group",-9)
    census_records = fillna_column(census_records,"number_of_cars_and_vans",-9)
    census_demographics = Demographics(VAR_CODE_CENSUS_2011_INIT)
    population = Population(census_demographics, census_records)

    if simplified:
        population.recode_variable(new_var_code_cate=VAR_CODE_CENSUS_2011_SIMPLIFIED,
                                   var_recode_map=VAR_RECODE_MAP_CENSUS_2011_INIT2SIMPLIFIED)

    return population
