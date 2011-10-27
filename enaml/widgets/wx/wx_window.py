#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_component import WXComponent
from .styling import compute_sizer_flags
from ..window import AbstractTkWindow

class WXWindow(WXComponent, AbstractTkWindow):
    """ A wxPython implementation of a Window.

    WXWindow uses a wx.Frame to create a simple top level window which
    contains other child widgets and layouts.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying wx.Frame control.

        """
        self.widget = wx.Frame(self.parent_widget())

    def initialize(self):
        """ Intializes the attributes on the wx.Frame.

        """
        super(WXWindow, self).initialize()
        shell = self.shell_obj
        self.set_title(shell.title)
        self.set_modality(shell.modality)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def show(self):
        """ Displays the window to the screen.

        """
        if self.widget:
            self.widget.Show()

    def hide(self):
        """ Hide the window from the screen.

        """
        if self.widget:
            self.widget.Hide()

    def shell_title_changed(self, title):
        """ The change handler for the 'title' attribute. Not meant for
        public consumption.

        """
        self.set_title(title)

    def shell_modality_changed(self, modality):
        """ The change handler for the 'modality' attribute. Not meant
        for public consumption.

        """
        self.set_modality(modality)

    def set_title(self, title):
        """ Sets the title of the frame. Not meant for public
        consumption.

        """
        if self.widget:
            self.widget.SetTitle(title)

    def set_modality(self, modality):
        """ Sets the modality of the frame. Not meant for public
        consumption.

        """
        # The wx frame cannot distinguish between application and
        # window modal (AFAIK). I think we need a wxDialog for that.
        if self.widget:
            if modality in ('application_modal', 'window_modal'):
                self.widget.MakeModal(True)
            else:
                self.widget.MakeModal(False)
