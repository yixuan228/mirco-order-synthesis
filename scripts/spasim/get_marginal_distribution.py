#!/usr/bin/env python
# coding: utf-8

import pandas as pd


# get marginal distribution_age
def marg_age_dist():
    age_data_file = "london_case/statistic_summary/inner_london_output_areas/2011_origin_data/age.csv"
    marg_age_all = pd.read_csv(age_data_file)

    marg_age_all["0-15"] = marg_age_all[list(map(str, range(0, 16)))].sum(axis="columns")
    marg_age_all["16-49"] = marg_age_all[list(map(str, range(16, 50)))].sum(axis="columns")
    marg_age_all["50+"] = marg_age_all[list(map(str, range(50, 90)))].sum(axis="columns")
    marg_age_all = marg_age_all[["GEO_CODE", "0-15", "16-49", "50+"]]
    age_0_sum=marg_age_all['0-15'].sum(axis=0)
    age_1_sum=marg_age_all['16-49'].sum(axis=0)
    age_2_sum=marg_age_all['50+'].sum(axis=0)
    age_sum_row={'0-15':age_0_sum,'16-49':age_1_sum,'50+':age_2_sum}
    # marg_age_all=marg_age_all.append(age_sum_row,ignore_index=True)
    marg_age_all = pd.concat([marg_age_all, pd.DataFrame([age_sum_row])], ignore_index=True)
    marg_age_all.set_index("GEO_CODE", inplace=True)
    marg_age_all = marg_age_all.div(marg_age_all.sum(axis=1), axis=0)
    marg_age_all.rename(columns={"0-15": 0, "16-49": 1, "50+": 2}, inplace=True)
    return marg_age_all


# get marginal distribution_sex
def marg_sex_dist():
    sex_data_file = "london_case/statistic_summary/inner_london_output_areas/2011_origin_data/sex.csv"
    marg_sex_all = pd.read_csv(sex_data_file)

    marg_sex_all = marg_sex_all[["GEO_CODE", "Males", "Females"]]
    marg_sex_all.set_index("GEO_CODE", inplace=True)
    marg_sex_all = marg_sex_all.div(marg_sex_all.sum(axis=1), axis=0)
    marg_sex_all.rename(columns={"Males": 0, "Females": 1}, inplace=True)
    return marg_sex_all


# get marginal distribution_ethnic
def marg_ethnic_dist():
    ethnic_data_file = "london_case/statistic_summary/inner_london_output_areas/2011_origin_data/ethnic_group.csv"
    marg_ethnic_all = pd.read_csv(ethnic_data_file)
    marg_ethnic_all.rename(columns={' White-Other White':'White-Other White'},inplace=True)

    marg_ethnic_all['White']=marg_ethnic_all[marg_ethnic_all.columns[[x.startswith("White") for x in marg_ethnic_all.columns]]].sum(axis='columns')
    marg_ethnic_all['Mixed']=marg_ethnic_all[marg_ethnic_all.columns[[x.startswith("Mixed") for x in marg_ethnic_all.columns]]].sum(axis='columns')
    marg_ethnic_all['Asian']=marg_ethnic_all[marg_ethnic_all.columns[[x.startswith("Asian") for x in marg_ethnic_all.columns]]].sum(axis='columns')
    marg_ethnic_all['Black']=marg_ethnic_all[marg_ethnic_all.columns[[x.startswith("Black") for x in marg_ethnic_all.columns]]].sum(axis='columns')
    marg_ethnic_all['Other']=marg_ethnic_all[marg_ethnic_all.columns[[x.startswith("Other") for x in marg_ethnic_all.columns]]].sum(axis='columns')
    marg_ethnic_all = marg_ethnic_all[["GEO_CODE", "White","Mixed", "Asian", "Black","Other"]]
    marg_ethnic_all.set_index("GEO_CODE", inplace=True)
    marg_ethnic_all=marg_ethnic_all.iloc[1:]
    marg_ethnic_all=marg_ethnic_all.div(marg_ethnic_all.sum(axis=1), axis=0)
    marg_ethnic_all.rename(columns={"White": 0, "Mixed": 1, "Asian": 2,"Black":3,"Other":4}, inplace=True)
    return marg_ethnic_all


# get marginal distribution_car_numbers
def marg_car_dist():
    car_number_data_file='london_case/statistic_summary/inner_london_output_areas/2011_origin_data/number_of_cars_and_vans.csv'
    marg_car_all=pd.read_csv(car_number_data_file,skiprows=1)
    marg_car_all.rename(columns={'Unnamed: 1':'GEO_CODE'},inplace=True)
    marg_car_all=marg_car_all[['GEO_CODE','0','1','2','3','4+']]
    marg_car_all.set_index("GEO_CODE", inplace=True)
    marg_car_all=marg_car_all.div(marg_car_all.sum(axis=1), axis=0)
    marg_car_all.rename(columns={'0':0,'1':1,'2':2,'3':3,'4+':4},inplace=True)
    return marg_car_all


# draw marginal distribution of online shopping frequency
# data from https://www.statista.com/forecasts/1241149/online-shopping-frequency-in-the-uk
# less often is interpreted as once every quarter
# data only consists of people age 16+, assuming people under 16 year-old do not shop online 
def marg_os_freq_dist(older_16):
    os_freq_dist = {1/7:0.28,0.5:0.24,2.5/30:0.24,1/30:0.1,1:0.07,0:0.02,1/91:0.05}
    age_16_plus=1-older_16 # which is derived from marg_age_all dataframe
    for key in os_freq_dist.keys():
        os_freq_dist[key]*=age_16_plus
    
    os_freq_dist[0]+=older_16
    return os_freq_dist

