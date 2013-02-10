#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import re
from types import MethodType
from weakref import ref

from .atom import Atom
from .members import Member
from .observer_pool import ObserverPool


class _MethodObserver(object):
    """ A small object which will wrap a bound method observer.

    This class is used internally by the `Observable` class.

    """
    __slots__ = ('im_func', 'im_selfref')

    def __init__(self, method):
        """ Initialize a MethodWrapper.

        Parameters
        ----------
        method : MethodType
            The bound method instance to wrap.

        """
        self.im_func = method.im_func
        self.im_selfref = ref(method.im_self)

    def __call__(self, change):
        """ Invoke the underlying method with the change object.

        """
        method = self._rebind_method()
        if method is not None:
            return method(change)

    def __eq__(self, other):
        """ Compare this wrapper for equality with other wrappers.

        """
        if isinstance(other, _MethodObserver):
            return self._rebind_method() == other._rebind_method()
        elif isinstance(other, MethodType):
            return self._rebind_method() == other
        return False

    def __nonzero__(self):
        """ Returns False if the underlying object was destroyed.

        This allows the observer to be automatically removed by the
        pool when it is no longer valid, without requiring several
        weakrefs enabled the observer to call back into the pool. This
        approach is far more memory efficient than the alternative.

        """
        return self.im_selfref() is not None

    def _rebind_method(self):
        """ Rebind the underlying method object.

        This will return None if the object is dead.

        """
        im_self = self.im_selfref()
        if im_self is not None:
            return MethodType(self.im_func, im_self, type(im_self))


class Observable(Atom):
    """ An `Atom` subclass which implements the observer pattern.

    """
    #: Private storage for the observer pool. The pool is created on the
    #: fly
    _observer_pool = Member()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def observe(self, name, callback, regex=False):
        """ Add an a callback to be notified when the atom changes.

        Callbacks are invoked in the order in which they are added. A
        given callback will not be added to the pool more than once,
        regardless of how many times `observe` is called.

        Callbacks will be automatically removed from the pool during a
        dispatch cycle if they evaluate to boolean False. This removes
        the need for keeping internal weakrefences to several objects
        in order to automatically unobserve.

        If the given callback is a bound method, it will be wrapped in
        a weak container. The owner of method must be weakref'able.

        Parameters
        ----------
        name : str
            The name of the member to observe on the atom.

        callback : callable
            A callable which will be invoked with a Change object when
            the member on the atom changes.

        regex : bool, optional
            If True, the `name` parameter is a regex string which is
            used to match against the available members. The callback
            will be notified when each matching member changes.

        """
        members = self.members()
        matches = []
        if regex:
            rgx = re.compile(name)
            for key in self.members():
                if rgx.match(key):
                    matches.append(key)
        elif name in members:
            matches.append(name)
        if len(matches) == 0:
            return
        pool = self._observer_pool
        if pool is None:
            self.enable_notifications()
            pool = self._observer_pool = ObserverPool()
        if isinstance(callback, MethodType):
            if callback.im_self is None:
                msg = 'Cannot use an unbound method as an observer.'
                raise TypeError(msg)
            callback = _MethodObserver(callback)
        for member_name in matches:
            self.enable_notifications(member_name)
            pool.add_observer(member_name, callback)

    def unobserve(self, name, callback, regex=False):
        """ Remove an observer from the observer pool.

        Parameters
        ----------
        name : str
            The name of the member for which the callback should be
            unsubscribed.

        callback : callable
            The callback which should be unsubscribed from the name.

        regex : bool, optional
            If True, the `name` parameter is a regex string which is
            used to match against the available members. The callback
            will be unsubscribed for each matching member name.

        """
        pool = self._observer_pool
        if pool is None:
            return
        if regex:
            rgx = re.compile(name)
            for key in self.members():
                if rgx.match(key):
                    pool.remove_observer(key, callback)
        else:
            pool.remove_observer(name, callback)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def notify(self, change):
        """ Handle the atom member change notification.

        This handler dispatches observers for the given name.

        """
        # Call super to behave well with multiple inheritance.
        super(Observable, self).notify(change)
        pool = self._observer_pool
        if pool is not None:
            pool.notify_observers(change.name, change)

