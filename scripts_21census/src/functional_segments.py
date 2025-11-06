#!/usr/bin/env python
# coding: utf-8

from shapely.geometry import Point
import numpy as np
import pandas as pd

# # population growth factor
# def get_new_pop(year): # year is relative to 2011. For example,year=1 indicates forecasting population in year 2012
#     # data from https://www.varbes.com/population/inner-london-population
#     annual_increase=[0,1.46,1.54,1.8,2,1.37,0.87,1.54,0.91,0.75,
#                      1.04,1.04,0.64,0.54,0.46,0.44,0.44,0.44,0.45,0.46,
#                      0.46,0.47,0.48,0.48,0.48,0.47,0.46,0.44,0.42,0.4,
#                      0.37,0.34,0.32]
#     increase_rate=[i/100 for i in annual_increase]
#     sex_data_file = "london_case/statistic_summary/inner_london_output_areas/2011_origin_data/sex.csv"
#     marg_sex_all = pd.read_csv(sex_data_file)

#     pop_size_all = marg_sex_all[["GEO_CODE", "Total"]]
#     pop_size_all.set_index("GEO_CODE", inplace=True)
    
#     if year < 0:
#         raise ValueError("year must be a non negative value")
#     elif year >=33:
#         raise ValueError("year must be smaller than 33, as the prediction only lasts to 2043")
#     else:
#         for i in range(year+1):
#             # pop_size_all['Total']*=(1+increase_rate[i])
#             pop_size_all.loc[:, 'Total'] *= (1 + increase_rate[i])
#         return pop_size_all.round()


# refined version
from shapely.geometry import Point
from shapely import vectorized
import numpy as np
import geopandas as gpd

def generate_random_points_in_polygon(polygon, num_points, crs='EPSG:27700'):
    minx, miny, maxx, maxy = polygon.bounds
    points = []

    while len(points) < num_points:
        xs = np.random.uniform(minx, maxx, num_points * 2)
        ys = np.random.uniform(miny, maxy, num_points * 2)
        mask = vectorized.contains(polygon, xs, ys)
        new_pts = [Point(x, y) for x, y, m in zip(xs, ys, mask) if m]
        points.extend(new_pts)

    # return points[:num_points]
    return gpd.GeoDataFrame(geometry=points[:num_points], crs=crs)


# convert aggregate population to dictionary form 
def aggregate_dict(df):
    agg_dict={}
    weight_list=list(df['weights'])
    columns=list(df.columns)
    columns.remove('weights')
    df=df[columns].astype(int)
    for i in range(df.shape[0]):
        agg_dict[tuple(df.loc[i,columns])]=weight_list[i]
    return agg_dict


# IPF
def IPF_Matrix(matrix,row_sum,col_sum):
    for i in range(50):
        # column update
        col_scalars = matrix.sum(axis=0) / col_sum
        matrix = (matrix / col_scalars)
        # row update
        row_scalars = matrix.sum(axis=1) / row_sum
        matrix = (matrix.T / row_scalars).T
    return matrix

