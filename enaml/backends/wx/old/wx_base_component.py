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
        shell = self.shell_obj
        self.set_enabled(shell.enabled)

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

    #--------------------------------------------------------------------------
    # Shell Object Change Handlers 
    #--------------------------------------------------------------------------
    def shell_enabled_changed(self, enabled):
        """ The change handler for the 'enabled' attribute on the shell 
        object.

        """
        self.set_enabled(enabled)

    def shell_bg_color_changed(self, color):
        """ The change handler for the 'bg_color' attribute on the shell
        object. Sets the background color of the internal widget to the 
        given color.
        
        """
        self.set_bg_color(color)

    def shell_fg_color_changed(self, color):
        """ The change handler for the 'fg_color' attribute on the parent.
        Sets the foreground color of the internal widget to the given color.
        For some widgets this may do nothing.
        """
        self.set_fg_color(color)

    def shell_font_changed(self, font):
        """ The change handler for the 'font' attribute on the shell 
        object. Sets the font of the internal widget to the given font.

        """
        self.set_font(font)

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

    def set_bg_color(self, color):
        """ Set the background color of the widget.

        """
        if not color:
            wx_color = wx.NullColour
        else:
            wx_color = wx.Colour(*color)
        self.widget.SetBackgroundColour(wx_color)

    def set_fg_color(self, color):
        """ Set the foreground color of the widget.

        """
        if not color:
            wx_color = wx.NullColour
        else:
            wx_color = wx.Colour(*color)
        self.widget.SetForegroundColour(wx_color)

    def set_font(self, font):
        pass

