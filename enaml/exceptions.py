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


class ShellExceptionContext(object):
    """ Context manager to that manages error state of shell objects.
    
    Any exceptions which occur within a with statement using this context
    will get swallowed and set into the exception trait of the shell object.
    
    """
    def __init__(self, shell_obj):
        self.shell_obj = shell_obj
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.shell_obj.exception = exc_value
        self.shell_obj.error = (exc_value is not None)
        if exc_value is not None:
            control_exception_handler = self.shell_obj.toolkit.control_exception_handler
            if control_exception_handler is not None:
                control_exception_handler(exc_value)
        return True


class ShellNotificationContext(ShellExceptionContext):
    """ Combination of a ShellExceptionContext and a notification_context
    
    Default behaviour is to use the null_handler with exceptions re-raised,
    which means any exceptions which occur during traits notification will be
    caught and set to the shell object's exception trait.
    
    """
    def __init__(self, shell_obj, handler=null_handler, reraise_exceptions=True,
            main=False, locked=False):
        self.shell_obj = shell_obj
        self.handler = handler
        self.reraise_exceptions = reraise_exceptions
        self.main = main
        self.locked = locked
    
    def __enter__(self):
        self.notification_handler = push_exception_handler(self.handler,
            self.reraise_exceptions, self.main, self.locked)
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pop_exception_handler()
        return super(ShellNotificationContext, self).__exit__(exc_type, exc_value, traceback)
    