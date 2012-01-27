#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
class Toolkit(dict):
    """ The Enaml Toolkit class which facilitates toolkit independent
    development. 

    The Toolkit is a dict subclass which is injected between the global 
    and builtin scopes of an executing an Enaml function or expression.
    The contents of the dictionary may consist of any useful objects
    that should be automatically in scope for executing Enaml code. 
    Typical content of a toolkit will include component constructors, 
    layout helpers, operators, and useful toolkit abstractions.

    """
    __stack__ = []

    __default_toolkit__ = None

    __toolkit_app__ = None

    @classmethod
    def active_toolkit(cls):
        """ A classmethod that returns the currently active toolkit,
        or the default toolkit if there is not active toolkit context.

        """
        stack = cls.__stack__
        if not stack:
            tk = cls.default_toolkit()
        else:
            tk = stack[-1]
        return tk

    @classmethod
    def default_toolkit(cls):
        """ A classmethod that returns the default toolkit, creating one
        if necessary.

        """
        tk = cls.__default_toolkit__
        if tk is None:
            from enaml import default_toolkit
            tk = cls.__default_toolkit__ = default_toolkit()
        return tk

    def __enter__(self):
        """ A context manager method that pushes this toolkit onto
        the active toolkit stack.

        """
        self.__stack__.append(self)

    def __exit__(self, exc_type, exc_value, traceback):
        """ A context manager method that pops this toolkit from the
        active toolkit stack.

        """
        self.__stack__.pop()

    def _get_toolkit_app(self):
        """ Returns the abstract toolkit app for this toolkit or
        raises an ValueError if one is not defined.

        """
        return self.__toolkit_app__

    def _set_toolkit_app(self, val):
        """ Sets the abstract toolkit app for this toolkit and makes
        it available in the toolkit's namespace under the 'toolkit_app'
        name.

        """
        self.__toolkit_app__ = val

    app = property(_get_toolkit_app, _set_toolkit_app)

