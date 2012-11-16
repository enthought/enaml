#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from types import MethodType
from weakref import ref


class WeakMethod(object):
    """ An object which weakly binds a method with a lifetime bound
    to the lifetime of the underlying object.

    Instances of WeakMethod are also weakref-able with a lifetime which
    is also bound to lifetime of the method owner.

    If multiple WeakMethods are requested for the same equivalent method
    object, the same WeakMethod will be returned. This behavior is the
    same as the standard weakref semantics.

    """
    __slots__ = ('_im_func', '_im_selfref', '_im_class', '__weakref__')

    #: An internal dict which maintains a strong reference to the
    #: the underlying weak method wrappers until the owner of the
    #: method is destroyed.
    _instances = {}

    @staticmethod
    def _remove(wr_item):
        """ A private weakref callback which will release the internal
        strong references to the WeakMethod instances for the object.

        """
        del WeakMethod._instances[wr_item]

    def __new__(cls, method):
        """ Create a new WeakMethod instance or return an equivalent
        which already exists.

        Parameters
        ----------
        method : A bound method object
            The bound method which should be wrapped weakly.

        """
        # The logic to setup the weakref is as follows:
        #
        # The keys of the instances dict should be weakrefs for a given
        # object and have a callback that will pop the item from the dict
        # when the underlying object is destroyed. When using weakrefs as
        # keys in a dictionary, two weakrefs will hash to the same value
        # and compare equally if their underlying object is the same. This
        # is true even if the two weakrefs have different callbacks. When
        # creating weakrefs without callbacks, Python will only create a
        # single instance for a given object, and return that same weakref
        # instance for multiple calls. i.e:
        #
        #     >>> f = Foo()
        #     >>> r = weakref.ref(f)
        #     >>> r is weakref.ref(f)
        #     True
        #
        # However, Python will create a new weakref instance for each
        # weakref with a callback, even if the callback is the same:
        #
        #     >>> def bar(): pass
        #     >>> f = Foo()
        #     >>> r = weakref.ref(f, bar)
        #     >>> r is weakref.ref(f, bar)
        #     False
        #
        # A WeakMethod instance does not rely on a callback. Therefore, a
        # good amount of space can be saved if all WeakMethod instances for
        # a given object share the same no-callback weakref for that object,
        # and the only weakref with callback kept around is the one used as
        # the key in the dict.
        #
        # The logic below first creates a no-callback weakref, which is always
        # necessary and will only be created by Python once and then reused.
        # That weakref is used to lookup the item in the dict. If that lookup
        # succeeds, the weakref with callback already exists and no more work
        # is required. Otherwise, the weakref with callback is created and
        # used as the key in the dict.
        im_selfref = ref(method.im_self)
        items = WeakMethod._instances.get(im_selfref)
        if items is None:
            items = []
            cbref = ref(method.im_self, WeakMethod._remove)
            WeakMethod._instances[cbref] = items
        im_func = method.im_func
        im_class = method.im_class
        for wm in items:
            if wm._im_func is im_func and wm._im_class is im_class:
                return wm
        self = super(WeakMethod, cls).__new__(cls)
        self._im_func = im_func
        self._im_selfref = im_selfref
        self._im_class = im_class
        items.append(self)
        return self

    def __call__(self, *args, **kwargs):
        """ Invoke the wrapped method by reconstructing the bound
        method from its components.

        If the underlying instance object has been destroyed, this
        method will return None.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to pass to the method.

        """
        im_self = self._im_selfref()
        if im_self is None:
            return
        method = MethodType(self._im_func, im_self, self._im_class)
        return method(*args, **kwargs)


# Use the faster version of WeakMethod if it's available.
try:
    from enaml.extensions.weakmethod import WeakMethod
except ImportError:
    pass

