from dtypes import TIMESTAMP_FLOAT32_DTYPE
import threading
import time
from locked_attributes import LockedAttributes


class DummyDataGenerator(LockedAttributes):
    """
    A dummy native feed which generates random values.
    """
    def __init__(self, frequency, saw_freq=30, dtype=TIMESTAMP_FLOAT32_DTYPE):
        LockedAttributes.__init__(self)
        self.callback = None
        self.go = True
        self.frequency = frequency
        self.saw_freq = saw_freq
        self.dtype = dtype
        self.call_count = 0
        self.first_time = time.time()

    def register_callback(self, callback):
        def inner(data_generator):
            while(self.go):
                timestamp = time.clock()
                val = (timestamp, timestamp % self.saw_freq)
                callback(val)
                time.sleep(1.0 / data_generator.frequency)
        thread = threading.Thread(target=inner, args=(self,))
        thread.daemon = True
        thread.start()

    def stop(self):
        self.go = False
