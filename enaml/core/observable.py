#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from bisect import insort
from collections import namedtuple
import re
from types import MethodType
from weakref import ref

from .atom import Atom
from .members import Member


class _BaseObserver(object):
    """ A base class for creating observer objects.

    This class is used internally by `Observable`.

    """
    __slots__ = ('data', 'callback')

    def __init__(self, data, callback):
        """ Initialize a _BaseObserver.

        Parameters
        ----------
        data : object
            The data to associate with the observer.

        callback : object
            The callback to associate with the observer.

        """
        self.data = data
        self.callback = callback

    def __lt__(self, other):
        """ A comparison method for the observer.

        This compares the underlying callbacks to allow the observer
        to be inserted into a list with ordering.

        """
        if isinstance(other, _BaseObserver):
            return self.callback < other.callback
        return False

    def match(self, name):
        """ Returns whether this observer matches the name.

        This method is abstract and must be implemented by subclasses.

        Parameters
        ----------
        name : str
            The name to match against the internal data.

        Returns
        -------
        result : bool
            Whether the given name matches the internal data. The
            semantic meaning of a match is decided by the subclass.

        """
        raise NotImplementedError


class _Observer(_BaseObserver):
    """ A `_BaseObserver` subclass which matches against a string.

    This class is used internally by `Observable`.

    """
    __slots__ = ()

    def match(self, name):
        """ Returns whether this observer matches the name.

        """
        return name == self.data


class _RegexObserver(_BaseObserver):
    """ A `_BaseObserver` subclass which matches against a regex.

    This class is used internally by `Observable`.

    """
    __slots__ = ()

    def match(self, name):
        """ Returns whether this observer matches the name.

        """
        return bool(self.data.match(name))


class _MethodWrapper(object):
    """ A small object which will wrap a bound method observer.

    This class is used internally by the `Observable` class.

    """
    __slots__ = ('im_func', 'im_class', 'im_selfref', 'ob_ref', '__weakref__')

    def __init__(self, method, observable):
        """ Initialize a MethodWrapper.

        Parameters
        ----------
        method : MethodType
            The bound method instance to wrap.

        observable : Observable
            The observable object which owns this wrapper.

        """
        def remove(wr, thisref=ref(self)):
            this = thisref()
            if this is not None:
                ob = this.ob_ref()
                if ob is not None:
                    ob.unobserve(this)
        self.im_func = method.im_func
        self.im_class = method.im_class
        self.im_selfref = ref(method.im_self, remove)
        self.ob_ref = ref(observable)

    def _rebind_method(self):
        """ Rebind the underlying method object. If the object is
        dead, this will return None.

        """
        im_self = self.im_selfref()
        if im_self is not None:
            return MethodType(self.im_func, im_self, self.im_class)

    def __call__(self, change):
        """ Invoke the underlying method with the change object.

        """
        method = self._rebind_method()
        if method is not None:
            return method(change)

    def __eq__(self, other):
        """ Compare this wrapper for equality with other wrappers.

        """
        if isinstance(other, _MethodWrapper):
            return self._rebind_method() == other._rebind_method()
        elif isinstance(other, MethodType):
            return self._rebind_method() == other
        return False


#: A namedtuple which holds information about a member change.
Change = namedtuple('Change', 'owner name old new')


class Observable(Atom):
    """ An `Atom` subclass which implements the observer pattern.

    """
    __slots__ = ('__weakref__',)

    #: Private storage for the list of observers. A flat list is used
    #: instead of a dict of lists to save space. The actual number of
    #: observers is usually small and scanning a small list is quick
    #: enough. The list is created on an as-needed basis.
    _observers = Member()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def observe(self, name, callback, regex=False, autoremove=True):
        """ Add a callback to observe changes on a member.

        Callback are executed according to their sorted order. If the
        given name does not reference a valid member, this is a no-op.

        Parameters
        ----------
        name : str
            The name of the member to observe on the atom.

        callback : callable
            A callable which takes a single argument which is a `Change`
            object representing the change to the atom.

        regex : bool, optional
            If True, `name` is a regex string which should be used to
            match against the changes. The default is False.

        autoremove : bool, optional
            If `callback` is a bound method and this flag is True, then
            the callback will be automatically removed when the owner
            of the the method is garbage collected. If this is False, a
            strong reference to be kept to the method until it is
            explicitly removed. The default is True.

        Returns
        -------
        result : bool
            True if the observer was added, False otherwise.

        """
        if isinstance(callback, MethodType) and autoremove:
            callback = _MethodWrapper(callback, self)
        members = type(self).members
        if regex:
            rgx = re.compile(name)
            observer = _RegexObserver(rgx, callback)
            has_match = False
            for key in members:
                if rgx.match(key):
                    has_match = True
                    self._set_member_notify_enabled(key, True)
            if not has_match:
                return False
        else:
            if name not in members:
                return False
            observer = _Observer(name, callback)
            self._set_member_notify_enabled(name, True)
        observers = self._observers
        if observers is None:
            observers = self._observers = []
            self._set_notify_enabled(True)
        insort(observers, observer)
        return True

    def unobserve(self, callback):
        """ Remove an observer from the observer pool.

        Parameters
        ----------
        callback : callable
            A callable which was previously registered via `observe`.

        Returns
        -------
        result : bool
            True if the callback was removed, False otherwise.

        """
        observers = self._observers
        if observers is not None:
            for observer in observers:
                if observer.callback == callback:
                    observers.remove(observer)
                    if len(observers) == 0:
                        self._observers = None
                    return True
        return False

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _notify(self, name, old, new):
        """ Handle the atom member change notification.

        This handler will dispatch any observers observing changes on
        the given member.

        """
        super(Observable, self)._notify(name, old, new)
        observers = self._observers
        if observers is not None and old != new:
            change = Change(self, name, old, new)
            for observer in observers:
                if observer.match(name):
                    observer.callback(change)

