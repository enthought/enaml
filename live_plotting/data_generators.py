from dtypes import DATETIME_FLOAT32_DTYPE
import numpy as np
import threading
from datetime import datetime


class DummyDataGenerator(object):
    """
    A dummy native feed which generates random values.
    """
    def __init__(self, time_period, dtype=DATETIME_FLOAT32_DTYPE):
        self.callback = None
        self.go = True
        self.time_period = time_period
        self.dtype = dtype

    def start(self, callback):
        def inner():
            val = np.empty(1, self.dtype)
            val['index'][0] = datetime.now()
            val['value'][0] = np.random.rand()
            callback(val)
            if self.go:
                threading.Timer(self.time_period, inner).start()
        threading.Timer(self.time_period, inner).start()

    def stop(self):
        self.go = False
