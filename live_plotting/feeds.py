import threading
from Queue import Queue
import unittest
from abc import ABCMeta, abstractmethod
import time
import numpy as np
from dtypes import DATETIME_FLOAT32_DTYPE
from data_generators import DummyDataGenerator
import zmq


class AbstractFeed(object):
    """
    Explicitly or implicitly maintains a queue.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        raise NotImplementedError


class QueueFeed(AbstractFeed):
    def __init__(self, native_feed, dtype=DATETIME_FLOAT32_DTYPE):
        self._queue = Queue()
        self.native_feed = native_feed
        self.dtype = dtype

    def start(self):
        self.native_feed.start(self._insert)

    def stop(self):
        self.native_feed.stop()

    def _insert(self, value):
        self._queue.put(value, True)

    def __len__(self):
        return self._queue.qsize()


class NumpyFeed(AbstractFeed):
    def __init__(self, native_feed, size=1000000, dtype=DATETIME_FLOAT32_DTYPE):
        self.native_feed = native_feed
        self._buffer = np.empty(size, dtype=dtype)
        self.size = size
        self.dtype = dtype
        self.index = 0
        self.lock = threading.Lock()

    def start(self):
        self.native_feed.start(self._insert)

    def stop(self):
        self.native_feed.stop()

    def _insert(self, value):
        with self.lock:
            self._buffer[self.index] = value
            self.index += 1
            if self.index >= self.size:
                raise BufferError

    def valid_slice(self):
        return self._buffer[:self.index]

    def __len__(self):
        return self.index


class ZeroMQFeed(AbstractFeed):
    def __init__(self, native_feed, host_spec="tcp://localhost:5555", size=1000000):
        self.native_feed = native_feed
        self.size = size
        self.host_spec = host_spec

    def start(self):
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.SUB)
        self.socket.connect(self.host_spec)

    def stop(self):
        raise NotImplementedError

    def __iter__(self):
        while True:
            try:
                contents = self.socket.recv(zmq.NOBLOCK)
                yield contents
            except:
                break


class TestFeed(object):
    def testDummyNative(self):
        self.feed.start()
        time.sleep(3)
        print 'Queue size is %s' % len(self.feed)
        self.assertTrue(len(self.feed) > 0, msg='Queue size is %s' % (len(self.feed)))


class TestQueueFeed(unittest.TestCase, TestFeed):
    def setUp(self):
        self.native_feed = DummyDataGenerator(1)
        self.feed = QueueFeed(self.native_feed)


class TestNumpyFeed(TestQueueFeed, TestFeed):
    def setUp(self):
        self.native_feed = DummyDataGenerator(1)
        self.feed = NumpyFeed(self.native_feed)


if __name__ == '__main__':
    unittest.main()
