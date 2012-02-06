#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from contextlib import contextmanager


class guard(object):
    """ A simple guard class that can be used to protect access 
    to arbitrary code.

    Example
    -------
    from enaml.guard import guard

    def foo():
        if not guard.guarded(bar):
            bar()
    
    def bar():
        with guard(bar):
            foo()

    """
    def __init__(self):
        self._counts = {}

    @contextmanager
    def __call__(self, *signature):
        """ Enter a guarded context for a given signature.

        Parameters
        ----------
        *signature
            Any number of positional arguments that forms the signature 
            of the guard. All of these arguments must be hashable.
        
        Returns
        -------
        result : context manager
            The 'with' statement context manager that handles the 
            lifetime of the guard.
        
        """
        counts = self._counts
        if signature in counts:
            counts[signature] += 1
        else:
            counts[signature] = 1
        try:
            yield self
        finally:
            counts[signature] -= 1
            if counts[signature] == 0:
                del counts[signature]
                
    def guarded(self, *signature):
        """ Check whether the given signature is currently guarded.

        Parameters
        ----------
        *signature
            Any number of positional arguments that forms the signature 
            of the guard. All of these arguments must be hashable.
        
        Returns
        -------
        result : bool
            Whether or not the signature is currently guarded.
        
        """
        return signature in self._counts


#: A singleton instance of the guard class. There is no need for more
#: than one.
guard = guard()


