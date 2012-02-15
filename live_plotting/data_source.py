from abc import ABCMeta, abstractmethod
from enaml.core.signaling import Signal
from buffer_op import BufferOp
from dtypes import DATETIME_FLOAT32_DTYPE
import numpy as np


class AbstractDataSource(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def dispatch(self, buffer):
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, callback):
        raise NotImplementedError

    @abstractmethod
    def unsubscribe(self, callback):
        raise NotImplementedError

    @abstractmethod
    def bind(self, publisher=None):
        raise NotImplementedError


class DataSource(BufferOp, AbstractDataSource):
    data = Signal()

    def __init__(self, dtype=DATETIME_FLOAT32_DTYPE, buffer_size=1000000, init_buffer=None, publisher=None,
                buffer_conversion_function=None, sample_probability=1.0, sample_fn=None, pass_through=True):
        BufferOp.__init__(self, sample_probability=sample_probability, sample_fn=sample_fn, pass_through=pass_through)
        self.buffer_conversion_function = buffer_conversion_function
        self.publisher = publisher
        self.buffer_size = buffer_size
        self._buffer = None

    def dispatch(self, data):
        buffer = data if self._buffer is None else np.concatenate((self._buffer, data))
        buffer = buffer[-self.buffer_size:]
        buffer = self.sample(buffer)
        if self.buffer_conversion_function:
            buffer = self.buffer_conversion_function(buffer)
        self._buffer = buffer
        self.data(buffer)

    def bind(self, publisher=None):
        if publisher:
            self.publisher = publisher
        self.publisher.subscribe(self.dispatch)

    def subscribe(self, callback):
        self.data.connect(callback)

    def unsubscribe(self, callback):
        self.data.disconnect(callback)
