#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode

from .widget_component import WidgetComponent


#: The standard attributes to proxy for a window component.
_WINDOW_PROXY_ATTRS = ['title']


class Window(WidgetComponent):
    """ A top-level Window component.

    A Window component is represents of a top-level visible component
    with a frame decoration. It may have at most one child widget which
    is expanded to fit the size of the window. It does not support
    features like MenuBars or DockPanes, for that, use a MainWindow.

    """
    #: The titlebar text.
    title = Unicode

    #: The initial size of the window. A value of (-1, -1) indicates
    #: to let the client choose the initial size
    # initial_size = SizeTuple

    #: The titlebar icon.
    # XXX needs to be implemented
    #icon = Instance()

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Window, self).bind()
        self.default_send(*_WINDOW_PROXY_ATTRS)

    def initial_attrs(self):
        """ Return the attr initialization dict for a window.

        """
        super_attrs = super(Window, self).initial_attrs()
        get = getattr
        attrs = dict((attr, get(self, attr)) for attr in _WINDOW_PROXY_ATTRS)
        super_attrs.update(attrs)
        return super_attrs

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def close(self):
        """ Send a 'close' command to the client UI

        """
        self.send({'action':'close'})

    def maximize(self):
        """ Send a 'maximize' command to the client UI.

        """
        self.send({'action':'maximize'})

    def minimize(self):
        """ Send a 'minimize' command to the client UI.

        """
        self.send({'action':'minimize'})

    def restore(self):
        """ Send a 'restore' command to the client UI.

        """
        self.send({'action':'restore'})

    def show(self):
        """ Send a 'show' command to the client UI.

        """
        self.visible = True
        self.send({'action':'show'})
