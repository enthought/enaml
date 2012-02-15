import threading
from abc import ABCMeta, abstractmethod
import numpy as np
from dtypes import DATETIME_FLOAT32_DTYPE
from enaml.core.signaling import Signal
from buffer_op import BufferOp
import time


class AbstractPublisher(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def bind(self):
        raise NotImplementedError

    @abstractmethod
    def unbind(self):
        raise NotImplementedError

    @abstractmethod
    def event_loop(self):
        raise NotImplementedError

    @abstractmethod
    def process_feed(self):
        raise NotImplementedError

    @abstractmethod
    def acquire_feed_data(self):
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, callback):
        raise NotImplementedError

    @abstractmethod
    def unsubscribe(self, callback):
        raise NotImplementedError


class Publisher(AbstractPublisher):

    def event_loop(self):
        def inner():
            buffer = self.process_feed()
            self.data(buffer)
            if self.go:
                threading.Timer(self.time_period, inner).start()
        threading.Timer(self.time_period, inner).start()


class NumpyPublisher(Publisher, BufferOp, AbstractPublisher):

    data = Signal()

    def __init__(self, data_feed, size=1000000, dtype=DATETIME_FLOAT32_DTYPE, sample_probability=1.0,
                sample_fn=None, pass_through=True, time_period=1 / 30.0, platform_event_loop=None):
        BufferOp.__init__(self, sample_probability=sample_probability, sample_fn=sample_fn, pass_through=pass_through)
        self.data_feed = data_feed
        self.time_period = time_period
        self.go = True
        self.buffer = None
        self._buffer = np.empty(size, dtype=dtype)
        self.size = size
        self.dtype = dtype
        self.index = 0
        self.lock = threading.Lock()
        # Should be a function which takes one argument - an object with the following defined attributes
        # 1) process_feed - a callable
        # 2) go - a boolean value
        # 3) time_period - A numeric value representing time in seconds
        # platform_event_loop should call obj.process_feed every obj.time_period seconds until
        # obj.go is true.
        self.platform_event_loop = None

    # Abstract API
    def bind(self):
        self.go = True
        self.data_feed.register_callback(self.insert)
        if self.platform_event_loop:
            self.platform_event_loop(self)
        else:
            self.event_loop()

    def unbind(self):
        self.data_feed.unregister_callback(self.insert)
        self.go = False

    def event_loop(self):
        super(NumpyPublisher, self).event_loop()

    def process_feed(self):
        with self.lock:
            #zch
            t_diff = time.time() - self.data_feed.first_time
            print 'rps: %s' % (self.data_feed.call_count / t_diff)
            data = self.acquire_feed_data()
            buffer = self.sample(data)
            self.index = 0
            return buffer

    def acquire_feed_data(self):
        valid_slice = np.copy(self.valid_slice())
        return valid_slice

    def subscribe(self, callback):
        self.data.connect(callback)

    def unsubscribe(self, callback):
        self.data.disconnect(callback)

    # NumpyPublisher specific methods
    def valid_slice(self):
        return self._buffer[:self.index]

    def insert(self, value):
        with self.lock:
            self._buffer[self.index] = value
            self.index += 1
            if self.index >= self.size:
                raise BufferError
