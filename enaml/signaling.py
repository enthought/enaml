#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from types import MethodType
from weakref import ref

from .callableref import CallableRef
from .weakmethod import WeakMethod


#: The key used to store the signals in an object's __dict__
_SIGNALS_KEY = '_[signals]'


class Signal(object):
    """ A descriptor which provides notification functionality similar
    to Qt signals and slots.

    A Signal is used by creating an instance in the body of a class
    definition. Slots (callables) are connected to the signal through
    the `connect` and `disconnect` methods. A signal can be emitted by
    calling the `emit` method passing arbitrary positional and keyword
    arguments.

    If a bound method is connected to a signal, then that slot will be
    automatically disconnected when the underlying object instance is
    garbage collected.

    """
    __slots__ = ()

    @staticmethod
    def disconnect_all(obj):
        """ Disconnect all slots connected to all signals on an object.

        Parameters
        ----------
        obj : object
            An object which has signals. Any slots connected to signals
            on this object will be disconnected.

        """
        dct = obj.__dict__
        key = _SIGNALS_KEY
        if key in dct:
            del dct[key]

    def __get__(self, obj, cls):
        """ The data descriptor getter.

        Returns
        -------
        result : Signal or BoundSignal
            If the descriptor is accessed through the class, then this
            Signal will be returned. Otherwise, a BoundSignal for the
            object will be returned.

        """
        if obj is None:
            return self
        return BoundSignal(self, ref(obj))

    def __set__(self, obj, val):
        """ The data descriptor setter.

        Attempting to assign to a Signal will raise an AttributeError.

        """
        raise AttributeError("can't set read only Signal")

    def __delete__(self, obj):
        """ The data descriptor deleter.

        This will disconnect all slots connected to this signal owned
        by the given object.

        """
        dct = obj.__dict__
        key = _SIGNALS_KEY
        if key not in dct:
            return
        signals = dct[key]
        if self not in signals:
            return
        del signals[self]
        if len(signals) == 0:
            del dct[key]


class _Disconnector(object):
    """ An object which disconnects a slot from a signal when the slot
    is garbage collected.

    This class is a private implementation detail of signaling and is
    not meant for public consumption.

    """
    __slots__ = ('_signal', '_objref')

    def __init__(self, signal, objref):
        """ Initialize a _Disconnector.

        Parameters
        ----------
        signal : Signal
            The Signal instance associated with this disconnector.

        objref : weakref
            A weak reference to the object which owns the signal.

        """
        self._signal = signal
        self._objref = objref

    def __call__(self, slot):
        """ Disconnect the slot from the signal.

        Parameters
        ----------
        slot : callable
            The slot to be disconnected from the signal.

        """
        obj = self._objref()
        if obj is None:
            return
        key = _SIGNALS_KEY
        dct = obj.__dict__
        if key not in dct:
            return
        signals = dct[key]
        signal = self._signal
        if signal not in signals:
            return
        slots = signals[signal]
        try:
            slots.remove(slot)
        except ValueError:
            pass
        else:
            # A _Disconnector is the first item in the list and is
            # created on demand. The list is deleted when that is the
            # only item remaining.
            if len(slots) == 1:
                del signals[signal]
                if len(signals) == 0:
                    del dct[key]


class BoundSignal(object):
    """ A bound Signal object.

    Instances of this class are created on the fly by a Signal. This
    class performs the actual work for connecting, disconnecting, and
    emitting signals.

    """
    __slots__ = ('_signal', '_objref')

    def __init__(self, signal, objref):
        """ Initialize a BoundSignal.

        Parameters
        ----------
        signal : Signal
            The Signal instance which created this BoundSignal.

        objref : weakref
            A weak reference to the object which owns the signal. The
            weakref should not have been created with a callback, as
            the internal implementation depends on the semantics of
            weakrefs created without callbacks.

        """
        self._signal = signal
        self._objref = objref

    def __eq__(self, other):
        """ Custom equality checking for a BoundSignal.

        A BoundSignal will compare equal to another BoundSignal if the
        unerlying Signal and object reference are equal. This equality
        is part of the mechanism which allows a signal to be connected
        to another signal.

        """
        if isinstance(other, BoundSignal):
            signal = self._signal
            objref = self._objref
            return signal is other._signal and objref is other._objref
        return False

    def __call__(self, *args, **kwargs):
        """ Custom call support for a BoundSignal.

        Calling a signal is indentical invoking the `emit` method. By
        making a signal callable, it is possible to directly connect
        a signal to another signal.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to pass to the slots
            connected to the signal.

        """
        self.emit(*args, **kwargs)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def emit(self, *args, **kwargs):
        """ Emit the signal with the given arguments and keywords.

        If a connected slot raises an exceptions, no further slots will
        be invoked and the exception will be bubbled up.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to pass to the slots
            connected to the signal.

        """
        obj = self._objref()
        if obj is None:
            return
        dct = obj.__dict__
        key = _SIGNALS_KEY
        if key not in dct:
            return
        signals = dct[key]
        signal = self._signal
        if signal not in signals:
            return
        # Make a copy of the list of slots since calling a slot has the
        # potential to modify the slots list. The first item in the list
        # is skipped since it is the disconnector for the signal. Putting
        # the disconnector in the list saves time and space.
        slots = signals[signal][1:]
        for slot in slots:
            slot(*args, **kwargs)

    def connect(self, slot):
        """ Connect the given slot to the signal.

        The slot will be called when the signal is emitted. It will be
        passed any positional and keyword arguments that were emitted
        with the signal. Multiple slots connected to a signal will be
        invoked in the order in which they were connected. Slots which
        are instance methods will be automatically disconnected when
        their underlying instance is garbage collected.

        Parameters
        ----------
        slot : callable
            The callable slot to invoke when the signal is emitted.

        """
        obj = self._objref()
        if obj is None:
            return
        dct = obj.__dict__
        key = _SIGNALS_KEY
        if key in dct:
            signals = dct[key]
        else:
            signals = dct[key] = {}
        signal = self._signal
        if signal in signals:
            slots = signals[signal]
            d = slots[0]
        else:
            d = _Disconnector(signal, self._objref)
            slots = signals[signal] = [d]
        if isinstance(slot, MethodType) and slot.im_self is not None:
            slot = CallableRef(WeakMethod(slot), d)
        slots.append(slot)

    def disconnect(self, slot):
        """ Disconnect the slot from the signal.

        If the slot was not previously connected, this is a no-op.

        Parameters
        ----------
        slot : callable
            The callable slot to disconnect from the signal.

        """
        if isinstance(slot, MethodType) and slot.im_self is not None:
            slot = CallableRef(WeakMethod(slot))
        _Disconnector(self._signal, self._objref)(slot)


# Use the faster version of signaling if it's available.
try:
    from enaml.extensions.signaling import Signal, BoundSignal, _Disconnector
except ImportError:
    pass

