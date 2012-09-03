#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from bisect import insort
from collections import namedtuple
from itertools import count
from types import MethodType
from weakref import ref, WeakKeyDictionary

from enaml.utils import WeakMethod


ConnItem = namedtuple('ConnItem', 'priority counter cb_ref dispatcher')


class Signal(object):
    """ A descriptor which provides notification functionality similar
    to Qt signals.

    A Signal is used by creating an instance in the body of a class
    definition. Connecting to the signal is done through an instance 
    of that class using the connect/disconnect methods. A signal is 
    emitted by calling the emit method with any given arguments.

    Only weak references are kept to the connected handlers. In the
    case of bound methods, the lifetime of the connection is tied
    to the lifetime of the underlying object and not the method 
    itself.
    
    """
    __slots__ = ('_instances',)

    def __init__(self):
        """ Initialize a Signal.

        """
        self._instances = WeakKeyDictionary()

    def __get__(self, obj, cls):
        """ The data descriptor getter. 

        Returns
        -------
        result : Signal or SignalInstance
            If the descriptor is accessed through the class, then this
            Signal will be returned. Otherwise, the SignalInstance for 
            the object will be returned.

        """
        if obj is None:
            return self
        instances = self._instances
        if obj in instances:
            res = instances[obj]
        else:
            res = instances[obj] = SignalInstance()
        return res

    def __set__(self, obj, val):
        """ The data descriptor setter. 

        Attempting to assign to a Signal will raise an AttributeError.

        """
        raise AttributeError("can't set read only Signal")
    
    def __delete__(self, obj):
        """ The data descriptor deleter. 

        This removes any SignalInstance for the given object, which will
        remove all connected handlers.

        """
        self._instances.pop(obj, None)


class SignalInstance(object):
    """ A signal implementation object. 

    Instances of this class are created on an as-needed basis by the
    Signal descriptor. A single instance of this class is created per
    instance of the class which owns the Signal descriptor. This class
    manages the actual connected handlers for the object.

    """
    __slots__ = ('_remove', '_counter', '_items', '__weakref__')
    
    def __init__(self):
        """ Initialize a SignalInstance.

        """
        def remove(cb_ref, thisref=ref(self)):
            this = thisref()
            if this is not None:
                this._remove_item(cb_ref)
        self._remove = remove
        self._counter = count(0)
        self._items = []

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _remove_item(self, cb_ref):
        """ Remove a connection from the list of items.

        Parameters
        ----------
        cb_ref : weakref
            A weak reference to the callback to remove from the list
            of connection items.

        """
        for item in self._items[:]:
            if item.cb_ref == cb_ref:
                self._items.remove(item)
                return

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def emit(self, *args, **kwargs):
        """ Emits the signal with the given arguments and keywords.

        """
        for item in self._items[:]:
            callback = item.cb_ref()
            if callback is not None:
                dispatcher = item.dispatcher
                if dispatcher is not None:
                    dispatcher(callback, *args, **kwargs)
                else:
                    callback(*args, **kwargs)

    def connect(self, callback, priority=0, dispatcher=None):
        """ Connects the given callback to the signal. 

        The callback will be called when the signal is emitted. It will 
        be passed any arguments that were emitted with the signal. A 
        callback can only be connected to the signal once. Multiple calls
        to connect() for the same callback will replace the previous 
        connection.

        Parameters
        ----------
        callback : callable
            The callable object to invoke whenever the signal is
            emitted. If the callback is not callable, and exception
            will be raised.

        priority : int, optional
            The priority for the connection. A connection with a 
            higher priority will be run first. The default priority
            is zero and negative priories are allowed.
        
        dispatcher : callable, optional
            An optional callable to use as the dispatcher for the 
            connection. If provided, it should accept 3 arguments:
            the callback for the connection, and the args and kwargs
            that should be passed to the callback.

        """
        if isinstance(callback, MethodType):
            cb_ref = ref(WeakMethod(callback), self._remove)
        else:
            cb_ref = ref(callback, self._remove)
        self._remove_item(cb_ref)
        counter = self._counter.next()
        conn = ConnItem(priority, counter, cb_ref, dispatcher)
        insort(self._items, conn)

    def disconnect(self, callback):
        """ Disconnects the given callback from the signal. 

        If the callback was not previously connected, this method has 
        no effect.

        Parameters
        ----------
        callback : callable
            The callable object to disconnect from the signal. If the
            callback is not callable, and exception will be raised.
        
        """
        if isinstance(callback, MethodType):
            cb_ref = ref(WeakMethod(callback))
        else:
            cb_ref = ref(callback)
        self._remove_item(cb_ref)

