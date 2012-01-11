#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref

import wx

from .styling import wx_color_from_color

from ..component import AbstractTkComponent


class WXComponent(AbstractTkComponent):
    """ Base component object for the Wx based backend.

    """
    #: The a reference to the shell object. Will be stored as a weakref.
    _shell_obj = lambda self: None

    #: The Wx widget created by the component
    widget = None

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

    def create(self, parent):
        """ Create the underlying Wx widget.

        """
        self.widget = wx.Panel(parent)

    def initialize(self):
        """ Initialize the attributes of the Wx widget.

        """
        shell = self.shell_obj
        if shell.bg_color:
            self.set_bg_color(shell.bg_color)
        if shell.fg_color:
            self.set_fg_color(shell.fg_color)
        if shell.font:
            self.set_font(shell.font)
        self.set_enabled(shell.enabled)

    def bind(self):
        """ Bind any event handlers for the Wx Widget. By default,
        this is a no-op. Subclasses should reimplement this method as
        necessary to bind any widget event handlers or signals.

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
        """ Sets the background color of the widget to an appropriate
        wxColour given the provided Enaml Color object.

        """
        wx_color = wx_color_from_color(color)
        self.widget.SetBackgroundColour(wx_color)

    def set_fg_color(self, color):
        """ Sets the foreground color of the widget to an appropriate
        wxColour given the provided Enaml Color object.

        """
        wx_color = wx_color_from_color(color)
        self.widget.SetForegroundColour(wx_color)

    def set_font(self, font):
        """ Sets the font of the widget to an appropriate wxFont given 
        the provided Enaml Font object.

        """
        # XXX implement me!
        pass

