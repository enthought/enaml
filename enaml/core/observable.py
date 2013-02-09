#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import namedtuple
from itertools import izip, islice
import re
from types import MethodType
from weakref import ref

from .atom import Atom
from .members import Member


class _ObserverMethodWrapper(object):
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
        if isinstance(other, _ObserverMethodWrapper):
            return self._rebind_method() == other._rebind_method()
        elif isinstance(other, MethodType):
            return self._rebind_method() == other
        return False

    def __nonzero__(self):
        """ Returns False if the underlying object was destroyed.

        """
        return self.im_selfref() is not None

    def _rebind_method(self):
        """ Rebind the underlying method object. If the object is
        dead, this will return None.

        """
        im_self = self.im_selfref()
        if im_self is not None:
            return MethodType(self.im_func, im_self, type(im_self))


def _pairwise(items):
    """ A simple iterator which yields pairs from a sequence.

    This function is used internally by `Observable`.

    """
    n = len(items)
    return izip(islice(items, 0, n, 2), islice(items, 1, n, 2))


#: A namedtuple which holds information about an atom member change.
Change = namedtuple('Change', 'owner name old new')


class ObserverList(object):

    __slots__ = ('_observers')

    def __init__(self):
        self._observers = []

    def _find_pool(self, name, create=False):
        observers = self._observers
        for idx, oname in enumerate(observers[::2]):
            if name == oname:
                return observers[idx * 2 + 1]
        if create:
            res = []
            observers.append(name)
            observers.append(res)
            return res

    def add(self, name, callback):
        pool = self._find_pool(name, True)
        if callback not in pool:
            pool.append(callback)

    def remove(self, name, callback):
        pool = self._find_pool(name)
        if pool is not None and callback in pool:
            pool.remove(callback)

    def notify(self, name, arg):
        pool = self._find_pool(name)
        if pool is not None:
            to_remove = []
            for callback in pool:
                if callback:
                    callback(arg)
                else:
                    to_remove.append(callback)
            for rem in to_remove:
                pool.remove(rem)


class Observable(Atom):
    """ An `Atom` subclass which implements the observer pattern.

    """
    #: Private storage for the observer pool.
    _observer_list = Member()

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
        in order to automatically unsubscribe.

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
        ob_list = self._observer_list
        if ob_list is None:
            self.enable_notifications()
            ob_list = self._observer_list = ObserverList()
        if isinstance(callback, MethodType):
            if callback.im_self is None:
                msg = 'Cannot use an unbound method as an observer.'
                raise TypeError(msg)
            callback = _ObserverMethodWrapper(callback)
        for member_name in matches:
            self.enable_notifications(member_name)
            ob_list.add(member_name, callback)

    def unobserve(self, name, callback, regex=False):
        """ Remove an observer from the observer pool.

        Parameters
        ----------
        name : str
            The name of the member for which the callback should be
            unsubscribed.

        callback : callable
            A callable which will be invoked with a Change object when
            the member on the atom changes.

        regex : bool, optional
            If True, the `name` parameter is a regex string which is
            used to match against the available members. The callback
            will be notified when each matching member changes.

        """

        ob_list = self._observer_list
        if ob_list is None:
            return
        if regex:
            rgx = re.compile(name)
            for key in self.members():
                if rgx.match(key):
                    ob_list.remove(key, callback)
        else:
            ob_list.remove(name, callback)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def notify(self, name, old, new):
        """ Handle the atom member change notification.

        This handler will dispatch any observers observing changes on
        the given member.

        """
        super(Observable, self).notify(name, old, new)
        ob_list = self._observer_list
        if ob_list is not None:
            change = Change(self, name, old, new)
            ob_list.notify(name, change)

