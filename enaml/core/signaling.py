#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from types import MethodType
from weakref import ref, WeakKeyDictionary


class Signal(object):
    """ A descriptor which provides notification functionality similar
    to Qt signals.

    A Signal is used by creating an instance of it in the body of a
    class definition. Connecting to the signal is done through an
    instance of that class using the connect/disconnect methods. A 
    signal is emitted by calling it with any given arguments. When 
    a signal is emitted, connect handlers are dispatched immediately
    with the arguments passed to the signal.

    Only weak references are kept to the connected handlers. In the
    case of bound methods, the lifetime of the connection is tied
    to the lifetime of the underlying object and not the method 
    itself.

    Example
    -------
        
        class Foo(object):
            bar = Signal()

        class Baz(object):
            def spam(self, *args, **kwargs):
                print 'spam called', args, kwargs
        
        def printer(*args, **kwargs):
            print 'printer called', args, kwargs

        >>> foo = Foo()
        >>> baz = Baz()
        >>> foo.bar.connect(printer)
        >>> foo.bar.connect(baz.spam)
        >>> foo.bar(42)
        printer called (42,) {}
        spam called (42,) {}
        >>> del baz
        >>> foo.bar(16, one=2)
        printer called (16,) {'one': 2}
        >>> foo.bar.disconnect(printer)
        >>> foo.bar(19)
    
    """
    __slots__ = ('_instances',)

    def __init__(self):
        self._instances = WeakKeyDictionary()

    def __get__(self, obj, cls):
        """ The data descriptors getter. Returns the _Signal instance
        for the given object, creating one if necessary. An error will
        be raised if the descriptor is accessed through the class.

        """
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
        """ The data descriptor setter. Raises an error when attempting
        to assign to a signal.

        """
        msg = 'Cannot set the value of a Signal. Signals are read-only.'
        raise AttributeError(msg)
    
    def __delete__(self, obj):
        """ The data descriptor deleter. Removes any _Signal instance
        for the given object, which will remove all connected handlers.

        """
        self._instances.pop(obj, None)


class _Signal(object):
    """ A signal implementation object. Instance of this class are
    created as needed by the Signal descriptor. A single instance 
    of this class is created per instance of the class which owns
    the Signal descriptor. This class manages the actual connected
    handlers for the object.

    """
    __slots__ = ('_connections', '__weakref__')
    
    def __init__(self):
        self._connections = []
    
    def _make_connection(self, callback):
        """ A private method which creates an appropriate connection 
        object for the given callback.

        Parameters
        ----------
        callback : callable
            The callable object which will be called when the signal
            is emitted.
        
        Returns
        -------
        result : _MethodConnection or _DirectConnection
            If the callable is a bound method, a _MethodConnection is
            created. For all other cases, a _DirectConnection is used.

        """
        if isinstance(callback, MethodType):
            connection = _MethodConnection(self, callback)
        else:
            connection = _DirectConnection(self, callback)
        return connection

    def _connection_dead(self, conn):
        """ A private method which removes the connection object from
        the internal list of connections when the connection has died.

        Parameters
        ----------
        conn : _BaseConnection
            The dead _BaseConnection instance to remove.

        """
        connections = self._connections
        if conn in connections:
            connections.remove(conn)

    def __call__(self, *args, **kwargs):
        """ Emits the signal with the given arguments and keywords.

        """
        for conn in self._connections:
            conn(args, kwargs)

    def connect(self, callback):
        """ Connects the given callback to the signal. The callback
        will be called when the signal is emitted. It will be passed
        any arguments that were emitted with the signal. A callback
        can only be connected to the signal once. Multiple calls to
        connect() for the same callback have no effect.

        Parameters
        ----------
        callback : callable
            The callable object to invoke whenever the signal is
            emitted. If the callback is not callable, and exception
            will be raised.
        
        """
        if not callable(callback):
            raise TypeError('Cannot connect a non-callable to a Signal')
        conn = self._make_connection(callback)
        connections = self._connections
        if conn not in connections:
            connections.append(conn)
    
    def disconnect(self, callback):
        """ Disconnects the given callback from the signal. If the 
        callback was not previously connected, this method has no
        effect.

        Parameters
        ----------
        callback : callable
            The callable object to disconnect from the signal. If the
            callback is not callable, and exception will be raised.
        
        """
        if not callable(callback):
            raise TypeError('Cannot disconnect a non-callable from a Signal')
        conn = self._make_connection(callback)
        self._connection_dead(conn)


class _BaseConnection(object):
    """ The base connection class which provides some basic lifetime
    management for the connection and stubs out the api which must
    be implemented by subclasses.

    """
    __slots__ = ('_parent_ref', '_remove', '__weakref__')

    def __init__(self, parent):
        """ Initialize a _BaseConnection

        Parameters
        ----------
        parent : _Signal
            The _Signal instance which owns this connection. Only a
            weak reference is maintained to the _Signal.

        """
        def remove(item, selfref=ref(self)):
            this = selfref()
            if this is not None:
                parent = self._parent_ref()
                if parent is not None:
                    parent._connection_dead(this)
        self._parent_ref = ref(parent)
        self._remove = remove
    
    def __call__(self, args, kwargs):
        """ Invokes the underlying callable with the given arguments
        and keywords.

        """
        raise NotImplementedError
    
    def __hash__(self):
        """ Computes the hash of the underlying callable. Two different
        connection instances with the same underlying callable should
        hash the same.

        """
        raise NotImplementedError
    
    def __eq__(self, other):
        """ Performs equality comparison. Two different connection
        instances with the same underlying callable should compare
        equally.

        """
        raise NotImplementedError


class _DirectConnection(_BaseConnection):
    """ A _BaseConnection subclass which makes a direct connection
    to the underlying callable.

    """
    __slots__ = ('_callback_ref',)

    def __init__(self, parent, callback):
        """ Initialize a _DirectConnection

        Parameters
        ----------
        parent : _Signal
            The _Signal instance which owns this connection. Only a
            weak reference is maintained to the _Signal.

        callback : callable
            The callable to which the connection should be made. 
            Only a direct weak reference to the callable is kept.

        """
        super(_DirectConnection, self).__init__(parent)
        self._callback_ref = ref(callback, self._remove)

    def __call__(self, args, kwargs):
        """ Invokes the underlying callable with the given arguments
        and keywords.

        """
        callback = self._callback_ref()
        if callback is not None:
            callback(*args, **kwargs)

    def __hash__(self):
        """ Computes and returns the hash of the weak reference to the
        underlying callable.

        """
        return hash(self._callback_ref)
    
    def __eq__(self, other):
        """ Performs equality comparison. If comparing against another
        instance of _DirectionConnection, the comparison is made between
        the weak references to the underlying callables. Otherwise, this
        method will return False.

        """
        if isinstance(other, _DirectConnection):
            return self._callback_ref == other._callback_ref
        return False
    

class _MethodConnection(_BaseConnection):
    """ A _BaseConnection subclass which makes a connection to the
    constituents of a bound method

    """
    __slots__ = ('_im_func', '_im_self_ref', '_im_class',)

    def __init__(self, parent, method):
        """ Initialize a _DirectConnection

        Parameters
        ----------
        parent : _Signal
            The _Signal instance which owns this connection. Only a
            weak reference is maintained to the _Signal.

        method : types.MethodType
            The bound method instance to which the connection should
            be made. The method is deconstructed into its constituents
            and the lifetime of connection is tied to the lifetime
            of the bound object. Only a weak reference to that object
            is kept.

        """
        super(_MethodConnection, self).__init__(parent)
        self._im_func = method.im_func
        self._im_self_ref = ref(method.im_self, self._remove)
        self._im_class = method.im_class

    def __call__(self, args, kwargs):
        """ Invokes the underlying method with the given arguments and 
        keywords. The bound method is reconstructed before being called.

        """
        im_self = self._im_self_ref()
        if im_self is not None:
            method = MethodType(self._im_func, im_self, self._im_class)
            method(*args, **kwargs)
    
    def __hash__(self):
        """ Computes and returns a hash of the consituent components
        of the underlying method.

        """
        return hash((self._im_func, self._im_self_ref, self._im_class))

    def __eq__(self, other):
        """ Performs equality comparison. If comparing against another
        instance of _MethodConnection, the comparison is made between
        the constituent components of the bound method. Otherwise, this
        method will return False.

        """
        if isinstance(other, _MethodConnection):
            return (self._im_func == other._im_func and
                    self._im_self_ref == other._im_self_ref and
                    self._im_class == other._im_class)
        return False

