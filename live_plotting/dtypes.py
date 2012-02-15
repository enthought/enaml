import numpy as np


DATETIME_FLOAT32_DTYPE = np.dtype([('index', np.datetime64), ('value', np.float32)])
TIMESTAMP_FLOAT32_DTYPE = np.dtype([('index', np.float64), ('value', np.float32)])

DTYPE_CONVERSION = {
    # Just a dummy entry to show signature.
    # Keys are of form (feed_dtype, subscription_dtype)
    # Values are functions that can map from feed_dtype to subscription_dtype
    (int, float): float

}
