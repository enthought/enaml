#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from weakref import ref


class CallableRef(object):
    """ An object which will weakly wrap a callable object.

    This class is useful when weakrefs to callable objects need to be
    used alongside regular callables. It exposes a callable interface
    which will dererence the underlying callable before calling it.

    """
    __slots__ = '_objref'

    def __init__(self, obj, callback=None):
        """ Initialize a CallableRef.

        Parameters
        ----------
        obj : callable
            The callable object which should be weakly wrapped.

        callback : callable or None
            An optional callable to invoke when the object has been
            garbage collected. It will be passed the weakref instance
            for associated with the dead object.

        Notes
        -----
        Instances of this class will compare equally to equivalent
        CallableRef instances as well as weakref instances which
        compare equally to the internal weakref.

        """
        self._objref = ref(obj, callback)

    def __eq__(self, other):
        """ Custom equality checking for a CallableRef.

        This will return True for an equivalent CallableRef *or* a
        weakref pointing to the same underlying callable.

        """
        if isinstance(other, CallableRef):
            return self._objref == other._objref
        if isinstance(other, ref):
            return self._objref == other
        return False

    def __call__(self, *args, **kwargs):
        """ Invoke the underlying callable.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to pass to the
            callable.

        Returns
        -------
        result : object
            The results of the callable, or None if it has already been
            garbage collected.

        """
        obj = self._objref()
        if obj is not None:
            return obj(*args, **kwargs)


# Use the faster version of CallableRef if it's available.
try:
    from enaml.extensions.callableref import CallableRef
except ImportError:
    pass

