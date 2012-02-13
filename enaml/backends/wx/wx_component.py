#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref

import wx

from ..component import AbstractTkComponent


class WXComponent(AbstractTkComponent):
    """ Base component object for the Wx based backend.

    """
    #: The a reference to the shell object. Will be stored as a weakref.
    _shell_obj = lambda self: None

    #: The Wx widget created by the component
    widget = None

    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying Wx widget. As necessary, subclasses
        should reimplement this method to create different types of
        widgets.

        """
        self.widget = wx.Panel(parent)

    def initialize(self):
        """ Initialize the attributes of the Wx widget.

        """
        super(WXComponent, self).initialize()
        self.set_enabled(self.shell_obj.enabled)

    def bind(self):
        """ Bind any event handlers for the Wx Widget. By default,
        this is a no-op. Subclasses should reimplement this method as
        necessary to bind any widget event handlers or signals.

        """
        super(WXComponent, self).bind()

    #--------------------------------------------------------------------------
    # Teardown Methods 
    #--------------------------------------------------------------------------
    def destroy(self):
        """ Destroy the underlying Wx widget.

        """
        widget = self.widget
        if widget:
            widget.Destroy()
    
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
    # Shell Object Change Handlers 
    #--------------------------------------------------------------------------
    def shell_enabled_changed(self, enabled):
        """ The change handler for the 'enabled' attribute on the shell 
        object.

        """
        self.set_enabled(enabled)

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_enabled(self, enabled):
        """ Enable or disable the widget.

        """
        self.widget.Enable(enabled)

    def set_visible(self, visible):
        """ Show or hide the widget.

        """
        self.widget.Show(visible)

