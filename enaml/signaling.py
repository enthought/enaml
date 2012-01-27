#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from types import MethodType
from weakref import ref, WeakKeyDictionary


class Signal(object):

    __slots__ = ('_instances',)

    def __init__(self):
        self._instances = WeakKeyDictionary()

    def __get__(self, obj, cls):
        if obj is None:
            msg = 'Signals can only be accessed through an instance'
            raise AttributeError(msg)
        instances = self._instances
        if obj in instances:
            res = instances[obj]
        else:
            res = instances[obj] = _Signal()
        return res

    def __set__(self, obj, val):
        msg = 'Cannot set the value of a Signal which is read-only'
        raise AttributeError(msg)
    
    def __delete__(self, obj):
        self._instances.pop(obj, None)


class _Signal(object):
    
    __slots__ = ('_connections', '__weakref__')
    
    def __init__(self):
        self._connections = []
    
    def _make_connection(self, callback):
        if isinstance(callback, MethodType):
            im_func = callback.im_func
            im_self = callback.im_self
            im_class = callback.im_class
            connection = _MethodConnection(self, im_func, im_self, im_class)
        else:
            connection = _DirectConnection(self, callback)
        return connection

    def _connection_dead(self, conn):
        connections = self._connections
        if conn in connections:
            connections.remove(conn)

    def __call__(self, *args, **kwargs):
        for conn in self._connections:
            conn(args, kwargs)

    def connect(self, callback):
        if not callable(callback):
            raise TypeError('Cannot connect non-callable to Signal')
        conn = self._make_connection(callback)
        connections = self._connections
        if conn not in connections:
            connections.append(conn)
    
    def disconnect(self, callback):
        conn = self._make_connection(callback)
        self._connection_dead(conn)


class _BaseConnection(object):

    __slots__ = ('_parent_ref', '_remove', '__weakref__')

    def __init__(self, parent):
        def remove(item, selfref=ref(self)):
            this = selfref()
            if this is not None:
                parent = self._parent_ref()
                if parent is not None:
                    parent._connection_dead(this)
        self._parent_ref = ref(parent)
        self._remove = remove
    
    def __call__(self, args, kwargs):
        raise NotImplementedError
    
    def __hash__(self):
        raise NotImplementedError
    
    def __eq__(self, other):
        raise NotImplementedError


class _DirectConnection(_BaseConnection):

    __slots__ = ('_callback_ref',)

    def __init__(self, parent, callback):
        super(_DirectConnection, self).__init__(parent)
        self._callback_ref = ref(callback, self._remove)

    def __call__(self, args, kwargs):
        callback = self._callback_ref()
        if callback is not None:
            callback(*args, **kwargs)

    def __hash__(self):
        return hash(self._callback_ref)
    
    def __eq__(self, other):
        if isinstance(other, _DirectConnection):
            return self._callback_ref == other._callback_ref
        return False
    

class _MethodConnection(_BaseConnection):

    __slots__ = ('_im_func', '_im_self_ref', '_im_cls',)

    def __init__(self, parent, im_func, im_self, im_cls):
        super(_MethodConnection, self).__init__(parent)
        self._im_func = im_func
        self._im_self_ref = ref(im_self, self._remove)
        self._im_cls = im_cls

    def __call__(self, args, kwargs):
        im_self = self._im_self_ref()
        if im_self is not None:
            method = MethodType(self._im_func, im_self, self._im_cls)
            method(*args, **kwargs)
    
    def __hash__(self):
        return hash((self._im_func, self._im_self_ref, self._im_cls))

    def __eq__(self, other):
        if isinstance(other, _MethodConnection):
            return (self._im_func == other._im_func and
                    self._im_self_ref == other._im_self_ref and
                    self._im_cls == other._im_cls)
        return False

