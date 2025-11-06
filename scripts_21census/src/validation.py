# define functions used to help with validation process

from collections import Counter
import pandas as pd

def get_stat_table_discrete(sample):
    value_counter = dict(Counter(sample))
    total = len(sample)
    table = pd.DataFrame.from_dict(value_counter, orient='index', columns=['count']).reset_index()
    table['count'] = table['count'].astype(int)
    table['frequency'] = round(table['count']/total, 4)

    table = table.T
    columns = table.iloc[0]
    table.columns = columns.astype(int)
    table.drop(table.index[0], inplace=True)

    table = table.reindex(sorted(table.columns), axis=1)

    table.rename(index={'count': 'Count', 'frequency': 'Frequency'}, inplace=True)
    table.columns.name = 'Value'

    return table


import numpy as np
from collections import Counter
from scipy.spatial.distance import jensenshannon

def freq_table(samples):
    """
    Count the frequency of each unique value in a 1D list of samples and normalize it to form a probability distribution.

    Parameters:
        samples (list): A list of discrete values (e.g., ['a', 'b', 'a', 'c']) representing samples from a discrete random variable.

    Returns:
        dict: A dictionary where keys are unique values from the input list,
              and values are their corresponding relative frequencies (probabilities).
              For example: {'a': 0.5, 'b': 0.33, 'c': 0.17}

    Notes:
        - The sum of all returned probabilities is 1.
        - The function assumes the input is from a single discrete random variable.
    """
    count = Counter(samples)
    total = len(samples)
    freq = {k: v / total for k, v in count.items()}
    return freq

def freq_table_2d(samples):
    """
    Count the joint frequency of pairs in a 2D list of samples and normalize to form a joint probability distribution.

    Parameters:
        samples (list of tuple): A list of 2D discrete sample pairs, such as [(x1, y1), (x2, y2), ...].

    Returns:
        dict: A dictionary where keys are (x, y) tuples representing joint values,
              and values are their normalized frequencies (joint probabilities).
              For example: {(1,2): 0.3, (2,2): 0.5, (1,3): 0.2}

    Notes:
        - The sum of all returned probabilities is 1.
        - The function assumes the input represents a sample from a joint distribution of two discrete random variables.
    """
    count = Counter(samples)
    total = len(samples)
    freq = {k: v / total for k, v in count.items()}
    return freq

def convert_freq_dict_to_vector(freq_dict, support):
    """
    Convert a frequency (probability) dictionary into a probability vector aligned with a predefined support.

    Parameters:
        freq_dict (dict): A dictionary of {value: frequency} or {value: probability}.
        support (list): A list of all possible values (support set) in the desired order.

    Returns:
        np.ndarray: A 1D NumPy array containing probabilities ordered according to the support.

    Notes:
        - If a support value is missing from freq_dict, its probability is assumed to be 0.
        - This function ensures both distributions are aligned for vector-based distance comparison (e.g. JS, KL).
    """
    return np.array([freq_dict.get(k, 0) for k in support])

def get_js_distance(p, q):
    """
    Compute the Jensen-Shannon distance between two probability vectors.

    Parameters:
        p (array-like): A 1D probability vector (e.g., numpy array or list) of length n, where all elements are ≥ 0 and sum to 1.
        q (array-like): Another 1D probability vector of the same length and constraints as p.

    Returns:
        float: The Jensen-Shannon distance, a value between 0 and 1.
               It is the square root of the Jensen-Shannon divergence.
               0 indicates identical distributions; 1 indicates complete dissimilarity.

    Raises:
        ValueError: If the input vectors are not the same length.

    Notes:
        - JS distance is symmetric and always finite.
        - Internally uses `scipy.spatial.distance.jensenshannon`, with log base 2.
    """
    return jensenshannon(p, q, base=2)
