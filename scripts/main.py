import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point

from spasim.synthesizer import IPF, SA
from spasim.basics import Constraints
from spasim.cases import simple_random_case, get_census_2011_base_population
import time
import pandas as pd
import geopandas as gpd
from spasim.functional_segments import get_new_pop, random_point_in_shp, aggregate_dict, IPF_Matrix
from spasim.get_marginal_distribution import marg_age_dist, marg_sex_dist,marg_ethnic_dist,marg_car_dist,marg_os_freq_dist


def main():
    ILA_gpd = inner_london_prediction()

    ILA_gpd.plot(column="os_freq",
                 legend=True,
                 scheme='percentiles',
                 cmap="YlOrRd",
                 figsize=(15, 10),
                 missing_kwds={
                     "color": "lightgrey",
                     "edgecolor": "red",
                     "hatch": "///",
                     "label": "Missing values", })
    plt.savefig("./london_case/results/heat_map.png",dpi=480)


def random_point_in_shp(shp):
    within = False
    while not within:
        x = np.random.uniform(shp.bounds[0], shp.bounds[2])
        y = np.random.uniform(shp.bounds[1], shp.bounds[3])
        within = shp.contains(Point(x, y))
    return Point(x,y)


def simple_test():
    # get base population and constraints
    base_pop, constraints = simple_random_case()

    # initialize synthesizers
    ipf_syn = IPF(base_pop.aggregate(), constraints)
    sa_syn = SA(base_pop, constraints, synthesis_size=300)

    # run and print results
    start = time.time()
    ipf_syn.synthesize(max_iter=50, stop_threshold=0.01)
    print("------------------------------------------------------")
    print("Results of IPF method:")
    print("Running Time:", time.time() - start)
    ipf_syn.describe_results()

    start = time.time()
    sa_syn.synthesize(max_iter=5000, init_temperature=1000, stop_threshold=0.01)
    print("------------------------------------------------------")
    print("Results of SA methods:")
    print("Running Time:", time.time() - start)
    sa_syn.describe_results()


def inner_london_prediction():
    # get base population
    inner_london_microdata_file = "london_case/census_microdata/census_microdata_2011_inner_london.csv"
    base_pop = get_census_2011_base_population(inner_london_microdata_file, simplified=True)
    base_pop = base_pop.select(["age", "sex","ethnic_group","number_of_cars_and_vans"])  # only use information we need to make prediction
    base_pop.recode_variable(new_var_code_cate={"age": {0: "0-15", 1: "16-49", 2: "50+"}},
                             var_recode_map={"age": {0: [0, ], 1: [1, 2], 2: [3, ]}})
    agg_base_pop = base_pop.aggregate()
    # when the condition is age=2,sex=0,ethnic_group=1,number_of_cars_and_vans=4, 
    # there is no record,thus agg_base_pop only has 149 rows rather than 150.

    # store weights of aggregate population into a dictionary
    agg_pop_dict=aggregate_dict(agg_base_pop.records)

    # get area_pop
    pop_size_all = get_new_pop(0)
    pop_size_all = pop_size_all.astype('Int64')

    # get marginal distributions
    marg_age_all=marg_age_dist()
    marg_sex_all=marg_sex_dist()
    marg_ethnic_all=marg_ethnic_dist()
    marg_car_all=marg_car_dist()
    os_freq_dist=marg_os_freq_dist(marg_age_all.iloc[-1,0])

    # get cost matrix
    cost_matrix = np.zeros((len(agg_pop_dict),len(os_freq_dist)))
    # assumptions: larger household size, adults, larger car ownership, female consumes more
    # needs more scientific background support
    # age = 0, cost = inf
    cost_matrix[0:50]=np.inf
    for i in range(50):
        cost_matrix[i][-2]=0.1
    # age = 1,cost = 1, age = 2, cost = 2
    # sex = 0,cost = 2, sex = 1, cost = 1
    # car = 0,cost = 5, car = 1, cost = 4, car = 2, cost = 3, car = 3, cost = 2, car = 4, cost = 1
    # map_age = {1:1,2:2}
    # map_sex = {0:2,1:1}
    # map_car = {0:5,1:4,2:3,3:2,4:1}
    for i in range(50,len(agg_pop_dict)):
        for j in range(len(os_freq_dist)):
            cost_matrix[i][j]=np.random.random()

    # matrix generation
    agg_pop_matrix = np.array([agg_pop_dict[key] for key in agg_pop_dict.keys()])
    agg_pop_matrix_T = np.array([agg_pop_matrix]).T
    os_freq_matrix = np.array([os_freq_dist[key] for key in os_freq_dist.keys()])
    os_freq_matrix = np.array([os_freq_matrix])
    init_matrix = agg_pop_matrix_T*os_freq_matrix/cost_matrix

    # matrix after IPF
    final_matrix=IPF_Matrix(init_matrix,1,list(os_freq_dist.values()))
    prob_matrix=np.array(list(os_freq_dist.values()))*final_matrix
    order_num_matrix=prob_matrix*np.array(list(os_freq_dist.keys()))
    order_sum_matrix=order_num_matrix.sum(axis=1)

    # personal attributes and online shopping frequency per day
    os_freq={}
    i=0
    for key in agg_pop_dict.keys():
        os_freq[key]=order_sum_matrix[i]
        i+=1

    # get polygons of OAs in Inner London Area (ILA)
    ILA_shp_file = "london_case/gis_files/boundaries/output_areas/inner_london_output_areas/england_oac_2011.shp"
    ILA_gpd = gpd.read_file(ILA_shp_file)
    ILA_gpd.to_crs(epsg='4326', inplace=True)
    ILA_gpd = ILA_gpd[["code", "geometry"]]
    ILA_gpd.set_index("code", inplace=True)
    ILA_gpd["os_freq"] = 0  # initialize online shopping frequency per day

    # generate synthetic population
    for area_code in ILA_gpd.index:
        if area_code in pop_size_all.index:
            area_pop_size = pop_size_all.loc[area_code]["Total"]
            area_constraint = Constraints(var_code_cate=base_pop.demographics.var_code_cate,
                                          var_marg_dist={"age": marg_age_all.loc[area_code].to_dict(),
                                                         "sex": marg_sex_all.loc[area_code].to_dict(),
                                                         "ethnic_group":marg_ethnic_all.loc[area_code].to_dict(),
                                                         "number_of_cars_and_vans":marg_car_all.loc[area_code].to_dict()})
            syn = IPF(base_population=agg_base_pop, constraints=area_constraint)
            area_syn_pop = syn.synthesize()
            area_os_freq = sum(area_syn_pop.records["weights"] * list(os_freq.values())) * area_pop_size
            ILA_gpd.loc[area_code, "os_freq"] = int(area_os_freq + 0.5)
        else:
            ILA_gpd.loc[area_code, "os_freq"] = -1
    
    ILA_gpd['os_freq'] = ILA_gpd['os_freq'].astype('Int64')
    # create empty list 
    ILA_gpd['points']=np.empty((len(ILA_gpd), 0)).tolist()
    # append randomly generated points into the list
    for index in range(ILA_gpd.shape[0]):
        for num in range(ILA_gpd['os_freq'][index]):
            ILA_gpd.iloc[index,2].append(random_point_in_shp(ILA_gpd['geometry'][index]))
    # convert missing data os_freq value back to nan from -1
    # ILA_gpd['os_freq'] = ILA_gpd['os_freq'].astype(str)
    # ILA_gpd['os_freq'] = ILA_gpd['os_freq'].replace('-1', np.nan)
    ILA_gpd['os_freq'] = ILA_gpd['os_freq'].replace(-1, np.nan)


    return ILA_gpd


if __name__ == '__main__':
    main()
