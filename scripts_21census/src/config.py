
from pathlib import Path

CURR_PATH       = Path(__file__).resolve().parent           # current file path (under src path)
SCRIPT_PATH     = CURR_PATH.parent                          # folder scripts_21census
REPO_PATH       = SCRIPT_PATH.parent                        # current repository path
SRC_PATH        = REPO_PATH / "scripts_21census" / 'src'

DATA_PATH       = REPO_PATH / "data"                        # path for saving the data
DATA_21CEN_PATH = REPO_PATH / 'data' / '2021-census-data'   # path for all census data related files
DATA_GIS_PATH   = REPO_PATH / "data" / 'gis-files'          # path for all gis files
DATA_ECB        = REPO_PATH / "data" / 'ecommerce-behavior' # path for all ecommerce related files

RESULTS_PATH    = REPO_PATH / "data" / 'results'            # path for all generated results

RES_STATIC          = RESULTS_PATH / 'static'                           # path for all intermediate results
RES_SYN_POP_PATH    = RESULTS_PATH / 'dynamic-synthetic-population'     # path for synthetic population results
# RES_SYN_POP_SAMPLE = RESULTS_PATH / 'dynamic-synthetic-population'/ 'sample_ver_1'  # debug use
RES_SYN_POP_SAMPLE  = RESULTS_PATH / 'static' / 'sample_population'
# RES_SYN_ORD_PATH    = RESULTS_PATH / 'dynamic-synthetic-order' / 'ver_1'         # path for synthetic order results
RES_SYN_ORD_PATH    = RESULTS_PATH / 'dynamic-synthetic-order'
RES_MAP_PATH        = RESULTS_PATH / 'dynamic-html-maps'                # path for visualization map results
