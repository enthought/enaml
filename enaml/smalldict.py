#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys


UOFFSET = 2 * sys.maxint + 2


class SmallDict(object):

    __slots__ = ('_data', '_free')

    def __init__(self):
        self._data = [NotImplemented] * 8
        self._free = 3

    def __len__(self):
        return len(self._data) * 3 / 8 - self._free

    def __sizeof__(self):
        return super(SmallDict, self).__sizeof__() + sys.getsizeof(self._data)

    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        return True

    def __getitem__(self, key):
        data = self._data
        h = hash(key)
        n = len(data) / 2
        i = h % n
        k = data[2 * i]
        if k == key:
            return data[2 * i + 1]
        null = NotImplemented
        if k is null:
            raise KeyError(key)
        if h < 0:
            h += UOFFSET
        perturb = h
        i = (5 * i + perturb + 1) % n
        while True:
            k = data[2  * i]
            if k == key:
                return data[2 * i + 1]
            if k is null:
                raise KeyError(key)
            perturb >>= 5
            i = (5 * i + perturb + 1) % n
        raise KeyError(key)

    def __setitem__(self, key, value):
        data = self._data
        null = NotImplemented
        if self._free == 0:
            ns = len(data) << 1
            self._data = [null] * ns
            self._free = ns * 3 / 8
            for k_, v_ in zip(data[::2], data[1::2]):
                if k_ is not null:
                    self[k_] = v_
            data = self._data
        h = hash(key)
        n = len(data) / 2
        i = h % n
        k = data[2 * i]
        if k is null or k == key:
            data[2 * i] = key
            data[2 * i + 1] = value
            self._free -= 1
            return
        if h < 0:
            h += UOFFSET
        perturb = h
        i = (5 * i + perturb + 1) % n
        while True:
            k = data[2 * i]
            if k is null or k == key:
                data[2 * i] = key
                data[2 * i + 1] = value
                self._free -= 1
                return
            perturb >>= 5
            i = (5 * i + perturb + 1) % n

    def __delitem__(self, key):
        data = self._data
        null = NotImplemented
        h = hash(key)
        n = len(data) / 2
        i = h % n
        k = data[2 * i]
        if k == key:
            data[2 * i] = null
            data[2 * i + 1] = null
            self._free += 1
            return
        if k is null:
            raise KeyError(key)
        if h < 0:
            h += UOFFSET
        perturb = h
        i = (5 * i + perturb + 1) % n
        while True:
            k = data[2 * i]
            if k == key:
                data[2 * i] = null
                data[2 * i + 1] = null
                self._free += 1
                return
            if k is null:
                raise KeyError(key)
            perturb >>= 5
            i = (5 * i + perturb + 1) % n

    def iteritems(self):
        null = NotImplemented
        data = self._data
        for idx in xrange(0, len(data), 2):
            try:
                k = data[idx]
                if k is not null:
                    yield (k, data[idx + 1])
            except IndexError:
                raise RuntimeError('dict changed size while iterating')

    def iterkeys(self):
        for k, ignored in self.iteritems():
            yield k

    def itervalues(self):
        for ignored, v in self.iteritems():
            yield v

    def keys(self):
        r = []
        push = r.append
        null = NotImplemented
        data = self._data
        for i in xrange(0, len(data), 2):
            k = data[i]
            if k is not null:
                push(k)
        return r

    def values(self):
        r = []
        push = r.append
        null = NotImplemented
        data = self._data
        for i in xrange(1, len(data), 2):
            k = data[i]
            if k is not null:
                push(k)
        return r

    def get(self, key, default=None):
        try:
            r = self[key]
        except KeyError:
            r = default
        return r

    def pop(self, key, default=None):
        try:
            r = self[key]
            del self[key]
        except KeyError:
            r = default
        return r

    def setdefault(self, key, default=None):
        try:
            r = self[key]
        except KeyError:
            r = self[key] = default
        return r

    def clear(self):
        self._data = [NotImplemented] * 8
        self._free = 3

    def has_key(self, key):
        return key in self

    def copy(self):
        r = SmallDict()
        r._data = self._data[:]
        r._free = self._free
        return r

    def popitem(self):
        null = NotImplemented
        data = self._data
        for idx in xrange(0, len(data), 2):
            k = data[idx]
            if k is not null:
                return data[idx + 1]
        raise ValueError('pop from empty dict')

