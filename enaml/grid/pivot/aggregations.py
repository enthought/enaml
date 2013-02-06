""" The canonical aggregations.
"""

from __future__ import with_statement

import numpy as np


def distinct(x):
    """ Count the unique items.
    """
    return len(np.unique(x))

def geo_mean(x):
    """ Return the geometric mean.
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.exp(np.log(x).mean())

# Map names to aggregation functions (or the strings that pandas accepts as
# such).
agg_funcs = dict(
    sum='sum',
    prod='prod',
    len=len,
    distinct=distinct,
    mean='mean',
    geo_mean=geo_mean,
    std='std',
    var='var',
    min='min',
    max='max',
)
