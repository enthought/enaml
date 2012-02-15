#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref

import wx

from ...components.base_widget_component import AbstractTkBaseWidgetComponent


class WXBaseWidgetComponent(AbstractTkBaseWidgetComponent):
    """ A Wx implementation of BaseWidgetComponent.

    """
    #: The a reference to the shell object. Will be stored as a weakref.
    _shell_obj = lambda self: None

    #: The Wx widget created by the component.
    widget = None

    @property
    def toolkit_widget(self):
        """ A property that returns the toolkit specific widget for this
        component.

        """
        return self.widget

    def _get_shell_obj(self):
        """ Returns a strong reference to the shell object.

        """
        return self._shell_obj()
    
    def _set_shell_obj(self, obj):
        """ Stores a weak reference to the shell object.

        """
        self._shell_obj = weakref.ref(obj)
    
    #: A property which gets a sets a reference (stored weakly)
    #: to the shell object
    shell_obj = property(_get_shell_obj, _set_shell_obj)

    def create(self, parent):
        """ Creates the underlying Wx object. As necessary, subclasses
        should reimplement this method to create different types of
        widgets.

        """
        self.widget = wx.EvtHandler()

    def initialize(self):
        """ Initializes the attributes of the the Wx widget.

        """
        super(WXBaseWidgetComponent, self).initialize()
    
    def bind(self):
        """ Bind any event handlers for the Wx Widget. By default, this
        is a no-op. Subclasses should reimplement this method as needed
        to bind any widget event handlers or signals.

        """
        super(WXBaseWidgetComponent, self).bind()

    def destroy(self):
        """ Destroy the underlying Wx widget.

        """
        widget = self.widget
        if widget:
            widget.Destroy()
        self.widget = None

