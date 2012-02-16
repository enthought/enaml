import threading
from abc import ABCMeta, abstractmethod
import numpy as np
from dtypes import TIMESTAMP_FLOAT32_DTYPE
from enaml.core.signaling import Signal
from buffer_op import BufferOp


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
                threading.Timer(1.0 / self.frequency, inner).start()
        threading.Timer(1.0 / self.frequency, inner).start()


class NumpyPublisher(Publisher, BufferOp):

    data = Signal()

    def __init__(self, data_feed, size=1000000, dtype=TIMESTAMP_FLOAT32_DTYPE, sample_probability=1.0,
                sample_fn=None, pass_through=True, frequency=30, platform_event_loop=None,
                mock_function=lambda timestamp, saw_freq: float(timestamp) % saw_freq
                ):
        BufferOp.__init__(self, sample_probability=sample_probability, sample_fn=sample_fn, pass_through=pass_through)
        self.data_feed = data_feed
        self.frequency = frequency
        self.go = True
        self._buffer = np.empty(size, dtype=dtype)
        self.size = size
        self.dtype = dtype
        self.index = 0
        self.mock_function = mock_function
        self.lock = threading.Lock()
        # Should be a function which takes one argument - an object with the following defined attributes
        # 1) process_feed - a callable
        # 2) go - a boolean value
        # 3) frequency - A numeric value representing frequency that this publisher will sample its feed in hertz
        # platform_event_loop should call obj.process_feed every 1.0 / obj.frequency seconds until
        # obj.go is true.
        self.platform_event_loop = None

    # Abstract API
    def bind(self):
        self.go = True
        self.data_feed.register_publisher(self.insert, self.mock_function)
        if self.platform_event_loop:
            self.platform_event_loop(self)
        else:
            self.event_loop()

    def unbind(self):
        self.go = False

    def event_loop(self):
        super(NumpyPublisher, self).event_loop()

    def process_feed(self):
        with self.lock:
            #print 'publisher.index', self.index
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
            self._buffer[self.index]['index'] = value[0]
            self._buffer[self.index]['value'] = value[1]
            self.index += 1
            if self.index >= self.size:
                raise BufferError
