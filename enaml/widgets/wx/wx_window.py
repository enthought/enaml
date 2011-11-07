#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_container import WXContainer
from .wx_component import WXComponent
from ..window import AbstractTkWindow

class WXWindow(WXContainer, AbstractTkWindow):
    """ A wxPython implementation of a Window.

    WXWindow uses a combined set of wx.Frame - wx.Window widget to create
    a simple top level window which contains other child widgets and
    layouts.

    Since it is a top_level container the WXWindow widget overides the
    generic container behaviour and returns resonable values instead of
    (-1, -1).

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying wx.Frame control.

        """
        style = (wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER |
                wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
        # FIXME: this is an ugly hack since the wx.Frame does not show
        # well. It is advised in the wxWidget documentation to add a
        # Panel or Window control before adding the children.
        self.frame = wx.Frame(self.parent_widget(), style=style)
        self.widget = wx.Window(self.frame)

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
        if self.frame:
            self.frame.Show()

    def hide(self):
        """ Hide the window from the screen.

        """
        if self.frame:
            self.frame.Hide()

    def shell_title_changed(self, title):
        """ The change handler for the 'title' attribute.

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
        if self.frame:
            self.frame.SetTitle(title)

    def set_modality(self, modality):
        """ Sets the modality of the frame. Not meant for public
        consumption.

        """
        # The wx frame cannot distinguish between application and
        # window modal (AFAIK). I think we need a wxDialog for that.
        if self.frame:
            if modality in ('application_modal', 'window_modal'):
                self.frame.MakeModal(True)
            else:
                self.frame.MakeModal(False)

    def size_hint(self):
        """ Window is a top level container and should return
            a resonable size hint.

        """
        return super(WXComponent, self).size_hint()