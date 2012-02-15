from dtypes import DATETIME_FLOAT32_DTYPE
import numpy as np
import threading
from datetime import datetime
import time


class DummyDataGenerator(object):
    """
    A dummy native feed which generates random values.
    """
    def __init__(self, time_period, dtype=DATETIME_FLOAT32_DTYPE):
        self.callback = None
        self.go = True
        self.time_period = time_period
        self.dtype = dtype
        self.call_count = 0
        self.first_time = time.time()

    def register_callback(self, callback):
        def inner(data_generator):
            while(self.go):
                data_generator.call_count += 1
                val = np.empty(1, data_generator.dtype)
                val['index'][0] = datetime.now()
                val['value'][0] = np.random.rand()
                callback(val)
                time.sleep(data_generator.time_period)
        thread = threading.Thread(target=inner, args=(self,))
        thread.start()

    def stop(self):
        self.go = False
