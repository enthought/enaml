#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref

import wx

from ..base_component import AbstractTkBaseComponent


class WXBaseComponent(AbstractTkBaseComponent):
    """ Base component object for the WxPython based backend.

    """
    #: The a reference to the shell object. Will be stored as a weakref.
    _shell_obj = lambda self: None

    #: The Wx widget created by the component
    widget = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying Wx widget.

        """
        self.widget = wx.Panel(parent)

    def initialize(self):
        """ Initialize the attributes of the Wx widget.

        """
        pass

    def bind(self):
        """ Bind any event handlers for the Wx Widget.

        """
        pass

    def destroy(self):
        """ Destroy the underlying Wx widget.

        """
        widget = self.widget
        if widget:
            widget.Destroy()

    def disable_updates(self):
        """ Disable rendering updates for the underlying Wx widget.

        """
        widget = self.widget
        if widget:
            if not widget.IsFrozen():
                widget.Freeze()
    
    def enable_updates(self):
        """ Enable rendering updates for the underlying Wx widget.

        """
        widget = self.widget
        if widget:
            if widget.IsFrozen():
                widget.Thaw()

    #--------------------------------------------------------------------------
    # Abstract Implementation 
    #--------------------------------------------------------------------------
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

