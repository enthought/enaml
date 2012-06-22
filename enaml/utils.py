#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" An amalgamation of utilities used throughout the Enaml framework.

"""
from types import MethodType
from weakref import ref


class abstractclassmethod(classmethod):
    """ A backport of the Python 3's abc.abstractclassmethod.

    """
    __isabstractmethod__ = True

    def __init__(self, func):
        func.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(func)


class WeakMethodWrapper(object):
    """ An object which weakly binds a method with a lifetime bound
    to the lifetime of the underlying object.

    """
    def __init__(self, method, default=None):
        """ Initialize a WeakMethodWrapper.

        Parameters
        ----------
        method : A bound method object
            The bound method which should be wrapped weakly.

        default : object, optional
            The default value to return if the underlying object for
            the method has been garbage colleced. Defaults to None.

        """
        self._im_func = method.im_func
        self._im_class = method.im_class
        self._im_self_ref = ref(method.im_self)
        self._default = default

    def __call__(self, *args, **kwargs):
        """ Invoke the wrapped method by reconstructing the bound
        method from its components.

        If the underlying instance object has been destroyed, this
        method will return the default value.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to pass to the method.

        """
        im_self = self._im_self_ref()
        if im_self is None:
            return self._default
        method = MethodType(self._im_func, im_self, self._im_class)
        return method(*args, **kwargs)
        
