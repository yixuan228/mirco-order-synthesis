import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
import pandas as pd

# Initial Random Sampler
rng = np.random.default_rng(seed=42)

# Frequency conversion table
freq_table = {
    "Freq": [
        "Several times a day",
        "Daily",
        "2-3 times a week",
        "Once a week",
        "2-3 times a month",
        "Once a month",
        "Several times a year",
        "Less often"
    ],
    "Orders_per_day": [3.0, 1.0, 2.5/7, 1/7, 2.5/30, 1/30, 5/365, 1/365],
    "Orders_per_week": [21.0, 7.0, 2.5, 1.0, 2.5/4.3, 1/4.3, 5/52, 1/52],
    "Orders_per_month": [90.0, 30.0, 10.7, 4.3, 2.5, 1.0, 0.42, 0.083]
}

freq_table = pd.DataFrame(freq_table)
# print(freq_table)


def predict_synpop_availability(rules, population):
    predicted_responses = []

    # Build the Fuzzy Logic System
    response_ctrl = ctrl.ControlSystem(rules)
    response_sim = ctrl.ControlSystemSimulation(response_ctrl)

    antecedent_features = [a.label for a in response_ctrl.antecedents]
    antecedent_features
    
    for _, person in tqdm(population.iterrows(), desc='Progressing', total=len(population)):
        # print(person)
        # print(person['sex'])
        for feature in antecedent_features:
            # print(feature)
            response_sim.input[feature] = person[feature]

        # simulation
        response_sim.compute()
        result = response_sim.output['response']
        # print(response_sim.output)
        result_01 = result / 100    # convert within 0-1

        # print(result)

        predicted_responses.append(result_01)

    return predicted_responses


import skfuzzy as fuzz
from skfuzzy import control as ctrl
from tqdm import tqdm

def predict_synpop_freq(rules, population, time_window='Orders_per_week'):
    """
    Returns
    -------
    predicted_dist : list of list of float
        A list where each element corresponds to an individual in the population,
        containing a normalized fuzzy membership distribution across frequency categories.

    predicted_e : list of float
        A list of expected frequency values computed as the dot product between the
        normalized fuzzy distribution and the numeric frequency table.
    """
    print(f'Frequency Expectation is within: {time_window}')
    freq_keys = list(rules.keys())

    ctrl_systems = [ctrl.ControlSystem(rules[key]) for key in freq_keys]
    response_sims = [ctrl.ControlSystemSimulation(cs) for cs in ctrl_systems]

    ante_features = 'age' # only consider age

    predicted_dist = [] # predicted frequency distribution
    predicted_e = []    # predicted frequency expectation

    for _, person in tqdm(population.iterrows(), desc='Progressing', total=len(population)):

        person_freq_dist = []

        for i, freq in enumerate(freq_keys):
            response_sim = response_sims[i]

            response_sim.input[ante_features] = person[ante_features]

            response_sim.compute()
            weight = response_sim.output['response']    # weight of each frequency   

            person_freq_dist.append(weight)

        # Normalize the frequency distribution
        total = sum(person_freq_dist)
        if total > 0:
            normalized_dist = [round(w / total, 4) for w in person_freq_dist]
        else:
            # Handle zero division: assign uniform distribution as fallback
            normalized_dist = [round(1 / len(person_freq_dist), 4)] * len(person_freq_dist)

        predicted_dist.append(normalized_dist)
        
        freq_expectation = np.dot(normalized_dist, freq_table[time_window])  # Expectation of frequency
        predicted_e.append(freq_expectation)
        # print(freq_expectation)

    return predicted_dist, predicted_e

# from tqdm import tqdm
# def predict_synord_category(rules, order_df):
    
#     rng = np.random.default_rng(seed=42)
#     cate_keys = list(rules.keys())
#     # print(cate_keys)

#     ctrl_systems = [ctrl.ControlSystem(rules[key]) for key in cate_keys]
#     response_sims = [ctrl.ControlSystemSimulation(cs) for cs in ctrl_systems]

#     ante_features = [[a.label for a in cs.antecedents] for cs in ctrl_systems]

#     predicted_dist = [] # predicted category distribution
#     predicted_cate = []

#     for row in tqdm(order_df.itertuples(index=False), desc='Progressing', total=len(order_df)):

#         person_cate_dist = []

#         for i, cate_key in enumerate(cate_keys):
#             response_sim = response_sims[i]

#             for feature in ante_features[i]:
#                 response_sim.input[feature] = getattr(row, feature)

#             response_sim.compute()
#             weight = response_sim.output['response']    # weight of each frequency   

#             person_cate_dist.append(weight)

#         # Normalize the frequency distribution
#         total = sum(person_cate_dist)
#         if total > 0:
#             normalized_dist = [w / total for w in person_cate_dist]
#         else:
#             normalized_dist = [1 / len(person_cate_dist)] * len(person_cate_dist)

#         normalized_round = [round(w, 4) for w in normalized_dist]

#         predicted_dist.append(normalized_round)

#         # Sample: Discrete Random Variable Sample
#         order_cate = rng.choice(len(cate_keys), p=normalized_dist)
#         predicted_cate.append(order_cate)

#     return predicted_dist, predicted_cate