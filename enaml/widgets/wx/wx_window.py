# -*- coding: UTF-8 -*-
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
    layouts. Because of this dual behaviour some enaml calls need
    to be delegated to the wx.Frame and some to the wx.Window.

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
        self._frame = wx.Frame(self.parent_widget(), style=style)
        self.widget = wx.Window(self._frame)

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
        self._frame.Show()

    def hide(self):
        """ Hide the window from the screen.

        """
        self._frame.Hide()

    def shell_title_changed(self, title):
        """ The change handler for the 'title' attribute.

        """
        self.set_title(title)

    def shell_modality_changed(self, modality):
        """ The change handler for the 'modality' attribute.
        """
        self.set_modality(modality)

    def set_title(self, title):
        """ Sets the title of the frame.

        """
        self._frame.SetTitle(title)

    def set_modality(self, modality):
        """ Sets the modality of the frame.

        """
        # FIXME: The wx frame cannot distinguish between application and
        # window modal.
        if modality in ('application_modal', 'window_modal'):
            self._frame.MakeModal(True)
        else:
            self._frame.MakeModal(False)

    def on_resize(self, event):
        """ Respond to a resize event.

        The method makes sure that after re-layout all the widgets are
        visible.

        """
        super(WXWindow, self).on_resize(event)
        self._frame.Fit()

    def size_hint(self):
        """ Return the sizehint for the WXWindow;

        Window is a top level container and should return a resonable size
        hint. Thus the WXComponent is used here to override the generic
        behaviour of WXContainers.
        """
        super(WXContainer, self).size_hint()
