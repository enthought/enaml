from dtypes import TIMESTAMP_FLOAT32_DTYPE
import threading
import time


class DummyDataGenerator(object):
    """
    A dummy native feed which generates random values.
    """
    def __init__(self, time_period, dtype=TIMESTAMP_FLOAT32_DTYPE):
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
                timestamp = time.time()
                val = (timestamp, timestamp % 30)
                callback(val)
                time.sleep(data_generator.time_period)
        thread = threading.Thread(target=inner, args=(self,))
        thread.daemon = True
        thread.start()

    def stop(self):
        self.go = False
