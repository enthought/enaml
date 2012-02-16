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
        self.registered_publishers = []
        self.saw_freq = saw_freq
        self.dtype = dtype
        self.call_count = 0
        self.first_time = time.time()

    def start(self):
        def inner(data_generator):
            while(self.go):
                time_stamp = time.clock()
                for publisher in self.registered_publishers:
                    notification_fn, value_fn = publisher[0], publisher[1]
                    notification_fn((time_stamp, value_fn(time_stamp, self.saw_freq)))
                time.sleep(1.0 / data_generator.frequency)
        thread = threading.Thread(target=inner, args=(self,))
        thread.daemon = True
        thread.start()

    def stop(self):
        self.go = False

    def register_publisher(self, notification_fn, value_function):
        self.registered_publishers.append((notification_fn, value_function))
