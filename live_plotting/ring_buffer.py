from dtypes import DATETIME_FLOAT32_DTYPE
import numpy as np
import unittest
from numpy import arange
import numpy


def length(val):
    return val.shape[0]


class CircularBuffer1d():

    def __init__(self, shape, dtype='f'):
        self.shape = shape
        self.array = numpy.zeros(shape, dtype=dtype)

    def __getitem__(self, sl):
        if type(sl) == int:
            return self.array[sl % self.shape[0]]
        elif type(sl) == slice:
            if sl.start is None:
                start = 0
            else:
                start = sl.start % self.shape[0]
            stop = sl.stop % self.shape[0]
            if stop > start:
                return self.array[start:stop]
            else:
                return numpy.concatenate((self.array[start:], self.array[: stop]), axis=0)

    def __setitem__(self, sl, a):
        if type(sl) == int:
            self.array[sl % self.shape[0]] = a
        elif type(sl) == slice:
            if sl.start is None:
                start = 0
            else:
                start = sl.start % self.shape[0]

            stop = sl.stop % self.shape[0]

            if stop > start:
                self.array[start:stop] = a
            else:
                self.array[start:] = a[:self.shape[0] - start]
                self.array[: a.shape[0] - (self.shape[0] - start)] = a[self.shape[0] - start:]


class RingBuffer(object):

    def __init__(self, num_elems, dtype=DATETIME_FLOAT32_DTYPE):
        self.size = num_elems + 1
        self.dtype = dtype
        #zch
        self._buffer = np.arange(num_elems)
        #self._buffer = np.empty(num_elems + 1, dtype=dtype)
        self.start = 0
        self.end = 0

    def write(self, value):
        if length(value) >= self.size:
            self.start = 0
            self.end = self.size - 1
            self._buffer[:] = value[-length(self._buffer):]
        else:
            if self.end + length(value) <= self.size:
                self._buffer[self.end:self.end + length(value)] = value
                new_end = self.end + length(value)
                if self.end < self.start <= new_end:
                    self.start = new_end + 1
                self.end = new_end
            else:
                pass
        print 'start: %s end: %s array: %s ' % (self.start, self.end, self._buffer)
        return self._buffer
        #self._buffer[self.end] = value
        #self.end = (self.end + 1) % self.size
        #if self.end == self.start:
        #    self.start = (self.start + 1) % self.size

    def pop(self):
        retval = self._buffer[self.start]
        self.start = (self.start + 1) % self.size
        return retval


class TestRingBuffer(unittest.TestCase):
    def setUp(self):
        self.buffer = RingBuffer(10)

    def testOne(self):
        self.buffer.write(arange(1))
        self.assertTrue(self.buffer.start == 0 and self.buffer.end == 1)

    def testTwo(self):
        self.buffer.write(arange(10))
        self.assertTrue(self.buffer.start == 0 and self.buffer.end == 10)


r = RingBuffer(10)

if __name__ == '__main__':
    unittest.main()
