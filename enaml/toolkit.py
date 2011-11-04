#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import os

from traits.api import HasStrictTraits, Callable, Str, WeakRef


class Constructor(HasStrictTraits):
    """ The constructor class to use to populate the toolkit.

    """
    #: A callable object which returns the shell class to use
    #: for the widget.
    shell_loader = Callable

    #: A callable object which returns the abstract implementation class
    #: to use for the widget.
    abstract_loader = Callable

    #: The key with which this constructor was added to the toolkit.
    #: It is set by the toolkit and used as the type name of the
    #: instantiated component.
    style_type = Str

    #: A reference (stored weakly) to the toolkit in which this
    #: constructor is contained. It is used to set the toolkit
    #: attribute on the components as they are created.
    toolkit = WeakRef('Toolkit')

    def __init__(self, shell_loader, abstract_loader):
        """ Initialize a constructor instance.

        Parameters
        ----------
        shell_loader : Callable
            A callable object which returns the shell class to use
            for the widget.

        abstract_loader : Callable
            A callable object which returns the abstract implementation
            class to use for the widget.

        """
        super(Constructor, self).__init__()
        self.shell_loader = shell_loader
        self.abstract_loader = abstract_loader

    def __enaml_call__(self, *args, **kwargs):
        """ Called by the vm to create the component(s) for this widget.
        This should not typically be overridden by sublasses. To perform
        specialized building behavior, override the `build` method.

        """
        component = self.build(*args, **kwargs)
        return ((component,), {})

    def build(self, *args, **kwargs):
        """ Calls the loaders and assembles the component.

        Subclasses should override this method to implement custom
        construction behavior if the default is not sufficient.

        Parameters
        ----------
        *args :
            Positional arguments with which this constructor was called
            from the enaml source code.
        **kwargs :
            Keyword arguments with which this constructor was called
            from the enaml source code.

        """
        shell_cls = self.shell_loader()
        abstract_cls = self.abstract_loader()
        component = shell_cls(style_type=self.style_type,
                              toolkit=self.toolkit,
                              abstract_obj=abstract_cls())
        return component

    def clone(self, shell_loader=None, abstract_loader=None):
        """ Creates a clone of this constructor, optionally changing
        out one or both of the loaders.

        """
        if shell_loader is None:
            shell_loader = self.shell_loader
        if abstract_loader is None:
            abstract_loader = self.abstract_loader
        return Constructor(shell_loader, abstract_loader)


class Toolkit(dict):
    """ The Enaml toolkit object class which facilitates easy gui
    toolkit independent backend development and use. The Toolkit
    is a dict subclass which is injected between the module and
    builtin scopes when executing an Enaml function or expression.

    XXX - more documentation

    """
    __stack__ = []

    __default__ = None

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
        tk = cls.__default__
        if tk is None:
            tk = cls.__default__ = default_toolkit()
        return tk

    def __init__(self, *args, **kwargs):
        """ Initialize a toolkit object using the same constructor
        signature as dict(). This overridden constructor ensures that
        the style types are properly assigned to the constructors.

        """
        super(Toolkit, self).__init__(*args, **kwargs)
        for key, value in self.iteritems():
            self[key] = value

    def __setitem__(self, key, value):
        """ Overridden dict.__setitem__ to apply style types to the
        constructors.

        """
        if isinstance(value, Constructor):
            # Clone the constructor so we don't risk the same constructor
            # being used by more than one toolkit and then having the
            # toolkit refs become out of sync.
            value = value.clone()
            value.style_type = key
            value.toolkit = self
        super(Toolkit, self).__setitem__(key, value)

    def update(self, other=None, **kwargs):
        """ Overridden from dict.update to apply style types to the
        constructors.

        """
        if other is None:
           pass
        elif hasattr(other, 'iteritems'):
            for k, v in other.iteritems():
                self[k] = v
        elif hasattr(other, 'keys'):
            for k in other.keys():
                self[k] = other[k]
        else:
            for k, v in other:
                self[k] = v
        if kwargs:
            self.update(kwargs)

    def setdefault(self, key, default=None):
        """ Overridden from dict.setdefault to apply style types to the
        constructors.

        """
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return default

    def __enter__(self):
        """ A context manager method that pushes this toolkit onto
        the active toolkit stack.

        """
        self.__stack__.append(self)

    def __exit__(self, *args, **kwargs):
        """ A context manager method that pops this toolkit from the
        active toolkit stack.

        """
        self.__stack__.pop()

    def _get_style_sheet(self):
        """ Returns the default style sheet instance for this toolkit.

        """
        return self['__style_sheet__']

    def _set_style_sheet(self, val):
        """ Sets the default style sheet instance for this toolkit.

        """
        self['__style_sheet__'] = val

    style_sheet = property(_get_style_sheet, _set_style_sheet)

    def _get_create_app(self):
        """ Returns the app creation function for this toolkit.

        """
        return self['__create_app__']

    def _set_create_app(self, val):
        """ Sets the app creation function for this toolkit.

        """
        self['__create_app__'] = val

    create_app = property(_get_create_app, _set_create_app)

    def _get_start_app(self):
        """ Returns the start app function for this toolkit.

        """
        return self['__start_app__']

    def _set_start_app(self, val):
        """ Sets the start app function for this toolkit.

        """
        self['__start_app__'] = val

    start_app = property(_get_start_app, _set_start_app)

    def _get_app(self):
        """ Returns the application object for this toolkit.

        """
        return self.get('__app__')

    def _set_app(self, val):
        """ Sets the application object for this toolkit.

        """
        self['__app__'] = val

    app = property(_get_app, _set_app)

    def _get_invoke_later(self):
        """ Returns the function for invoking a function later in the event
        loop.

        """
        return self.get('__invoke_later__')

    def _set_invoke_later(self, val):
        self['__invoke_later__'] = val

    invoke_later = property(_get_invoke_later, _set_invoke_later)


def default_toolkit():
    """ Creates an returns the default toolkit object based on
    the user's current ETS_TOOLKIT environment variables.

    """
    toolkit = os.environ.get('ETS_TOOLKIT', 'qt').lower()

    if toolkit == 'qt' or toolkit == 'qt4':
        return qt_toolkit()

    if toolkit == 'wx':
        return wx_toolkit()

    raise ValueError('Invalid Toolkit: %s' % toolkit)


def qt_toolkit():
    """ Creates and return a toolkit object for the Qt backend.

    """
    from .operators import OPERATORS
    from .widgets.qt.constructors import QT_CONSTRUCTORS
    from .util.guisupport import get_app_qt4, start_event_loop_qt4
    from .widgets.qt.styling import QT_STYLE_SHEET
    from .widgets.qt.utils import invoke_later
    from .widgets.layout.layout_helpers import LAYOUT_HELPERS

    utils = {}

    toolkit = Toolkit(QT_CONSTRUCTORS)

    toolkit.create_app = get_app_qt4
    toolkit.start_app = start_event_loop_qt4
    toolkit.style_sheet = QT_STYLE_SHEET
    toolkit.invoke_later = invoke_later
    toolkit.update(utils)
    toolkit.update(OPERATORS)
    toolkit.update(LAYOUT_HELPERS)

    return toolkit


def wx_toolkit():
    """ Creates and return a toolkit object for the Wx backend.

    """
    from .operators import OPERATORS
    from .widgets.wx.constructors import WX_CONSTRUCTORS
    from .util.guisupport import get_app_wx, start_event_loop_wx
    from .widgets.wx.styling import WX_STYLE_SHEET
    from .widgets.wx.utils import invoke_later
    from .widgets.layout.layout_helpers import LAYOUT_HELPERS

    utils = {}

    toolkit = Toolkit(WX_CONSTRUCTORS)

    toolkit.create_app = get_app_wx
    toolkit.start_app = start_event_loop_wx
    toolkit.style_sheet = WX_STYLE_SHEET
    toolkit.invoke_later = invoke_later
    toolkit.update(utils)
    toolkit.update(OPERATORS)
    toolkit.update(LAYOUT_HELPERS)

    return toolkit

