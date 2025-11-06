import dask.dataframe as dd
import osmnx as ox
import geopandas as gpd
from shapely.ops import unary_union


def census_microdata_filtering():
    """extract records from the whole census microdata with selected areas and variables"""
    origin_microdata_file = "london_case/census_microdata/isg_regionv2.tab"
    filtered_microdata_file = "london_case/census_microdata/census_microdata_2011_inner_london.csv"
    variable_rename_map = {"age": "age",
                           "sex": "sex",
                           "sizhuk": "household_size",
                           "langprf": "english_proficiency",
                           "marstat": "marital_status",
                           "carsnoc": "number_of_cars_and_vans",
                           "ecopuk": "economic_activity",
                           "ethnicityew": "ethnic_group",
                           "hlqupuk11": "highest_qualification",
                           "scgpuk11c": "approximated_social_grade"}

    ddf_all = dd.read_table(origin_microdata_file)
    ddf_filtered = ddf_all[ddf_all["region"] == 7]  # filter regions (7 is the code for inner london)
    ddf_filtered = ddf_filtered[list(variable_rename_map.keys())]  # filter variables
    ddf_filtered = ddf_filtered.rename(columns=variable_rename_map)
    df_filtered = ddf_filtered.compute()
    df_filtered.to_csv(filtered_microdata_file, index=False)


def get_osm_data():
    london_wards_shpfile = "london_case/london_case/gis_files/London-wards-2018_ESRI/London_Ward.shp"
    gdf_london_wards = gpd.read_file(london_wards_shpfile)
    gdf_london_wards.to_crs(epsg='4326', inplace=True)
    # london_wards_codes = gdf_london_wards[["DISTRICT", "LAGSSCODE"]].drop_duplicates()

    case_area_boroughs_names = ["Ealing", ]
    gdf_case_boroughs = gdf_london_wards[gdf_london_wards["DISTRICT"].isin(case_area_boroughs_names)]
    case_area_polygon = unary_union(gdf_case_boroughs["geometry"])

    # download land-use data of case-study area
    gdf_case_areas = ox.geometries.geometries_from_polygon(case_area_polygon,tags={"landuse":["residential","retail","commercial"]})
    gdf_case_areas[["name","landuse","geometry","type"]].to_file("./london_case/london_case/")

    # download residential building data of case-study area
    gdf_case_areas = ox.geometries.geometries_from_polygon(case_area_polygon, tags={"building": ["residential"]})

    # download road network of case-study area and parse it to networkx graph
    G = ox.graph_from_polygon(case_area_polygon,
                              custom_filter="['highway'~'motorway|trunk|primary|secondary|tertiary|residential']")
    ox.io.save_graph_geopackage(G, filepath=None, encoding='utf-8', directed=False)
