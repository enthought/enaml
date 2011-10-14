#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
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

