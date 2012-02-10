from abc import ABCMeta, abstractmethod
from enaml.core.signaling import Signal


class AbstractDataSource(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def dispatch(self, buffer):
        raise NotImplementedError

    @abstractmethod
    def pack_buffer(self, buffer):
        raise NotImplementedError


class DataSource(AbstractDataSource):
    data = Signal()

    def __init__(self, packing_fn=None):
        self.packing_fn = packing_fn

    def pack_buffer(self, buffer):
        retval = buffer if self.packing_fn is None else self.packing_fn(buffer)
        return retval

    def dispatch(self, buffer):

        buffer = self.pack_buffer(buffer)
        print 'dispatch', buffer.shape
        self.data(buffer)
