#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref

from .qt import QtGui
from .styling import q_color_from_color, q_font_from_font

from ..base_component import AbstractTkBaseComponent


class QtBaseComponent(AbstractTkBaseComponent):
    """ Base component object for the Qt based backend.

    """
    #: The a reference to the shell object. Will be stored as a weakref.
    _shell_obj = lambda self: None

    #: The Qt widget created by the component
    widget = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------    
    def create(self, parent):
        """ Create the underlying Qt widget.

        """
        self.widget = QtGui.QFrame(parent)

    def initialize(self):
        """ Initialize the attributes of the Qt widget.

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
        """ Bind any event/signal handlers for the Qt Widget.

        """
        pass

    def destroy(self):
        """ Destroy the underlying Qt widget.

        """
        widget = self.widget
        if widget:
            # On Windows, it's not sufficient to simply destroy the
            # widget. It appears that this only schedules the widget 
            # for destruction at a later time. So, we need to explicitly
            # unparent the widget as well.
            widget.setParent(None)
            widget.destroy()

    def disable_updates(self):
        """ Disable rendering updates for the underlying Qt widget.

        """
        widget = self.widget
        if widget:
            widget.setUpdatesEnabled(False)

    def enable_updates(self):
        """ Enable rendering updates for the underlying Wx widget.

        """
        widget = self.widget
        if widget:
            widget.setUpdatesEnabled(True)

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
        """ The change handler for the 'fg_color' attribute on the shell
        object. Sets the foreground color of the internal widget to the 
        given color.

        """
        self.set_fb_color(color)

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
        widget = self.widget
        if widget:
            widget.setEnabled(enabled)

    def set_visible(self, visible):
        """ Show or hide the widget.

        """
        widget = self.widget
        if widget:
            widget.setVisible(visible)

    def set_bg_color(self, color):
        """ Set the background color of the widget.

        """
        widget = self.widget
        if widget:
            role = widget.backgroundRole()
            if not color:
                palette = QtGui.QApplication.instance().palette(widget)
                qcolor = palette.color(role)
                # On OSX, the default color is rendered *slightly* off
                # so a simple workaround is to tell the widget not to
                # auto fill the background.
                widget.setAutoFillBackground(False)
            else:
                qcolor = q_color_from_color(color)
                # When not using qt style sheets to set the background
                # color, we need to tell the widget to auto fill the 
                # background or the bgcolor won't render at all.
                widget.setAutoFillBackground(True)
            palette = widget.palette()
            palette.setColor(role, qcolor)
            widget.setPalette(palette)
    
    def set_fg_color(self, color):
        """ Set the foreground color of the widget.

        """
        widget = self.widget
        if widget:
            role = widget.foregroundRole()
            if not color:
                palette = QtGui.QApplication.instance().palette(widget)
                qcolor = palette.color(role)
            else:
                qcolor = q_color_from_color(color)
            palette = widget.palette()
            palette.setColor(role, qcolor)
            widget.setPalette(palette)

    def set_font(self, font):
        """ Set the font of the underlying toolkit widget to an 
        appropriate QFont.

        """
        widget = self.widget
        if widget:
            q_font = q_font_from_font(font)
            widget.setFont(q_font)

