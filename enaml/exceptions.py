#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from contextlib import contextmanager
from traits.api import push_exception_handler, pop_exception_handler

class EnamlError(Exception):
    """ A general exception used to indicate an error with Enaml or 
    the Enaml runtime that doesn't fit the semantics of any other 
    Python standard exception.

    """
    pass


class EnamlSyntaxError(EnamlError):
    """ Derived from EnamlError and used to indicate an Error in the
    syntax of a .enaml file.

    """
    pass


class EnamlRuntimeError(EnamlError):
    """ An EnamlError that occurs during the execution of an Enaml 
    script that couldn't be caught at compile time but prevents the 
    runtime from continuing to execute the script.

    """
    pass


def null_handler(obj, trait, old, new):
    """ A null Traits exception handler.
    """
    pass

@contextmanager
def notification_context(handler=null_handler, reraise_exceptions=True, main=False, locked=True):
    """ Context manager to temporarily add a TraitsExceptionHandler
    
    We use a context manager to ensure that the exception handler gets cleared
    no matter what.  Default behaviour is to use the null_handler with
    exceptions re-raised, which means any exceptions which occur will be passed
    through.
    """
    yield push_exception_handler(handler, reraise_exceptions, main, locked)
    pop_exception_handler()
