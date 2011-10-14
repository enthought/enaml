#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from traits.api import implements

from .wx_component import WXComponent
from .styling import compute_sizer_flags

from ..window import IWindowImpl

from ...enums import Modality


class WXWindow(WXComponent):
    """ A wxPython implementation of a Window.

    WXWindow uses a wx.Frame to create a simple top level window which
    contains other child widgets and layouts.

    See Also
    --------
    Window

    """
    implements(IWindowImpl)

    #---------------------------------------------------------------------------
    # IWindowImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying wx.Frame control.

        """
        self.widget = wx.Frame(self.parent_widget())

    def initialize_widget(self):
        """ Intializes the attributes on the wx.Frame.

        """
        self.set_title(self.parent.title)
        self.set_modality(self.parent.modality)

    def create_style_handler(self):
        """ Creates and sets the window style handler.

        """
        pass
        
    def layout_child_widgets(self):
        """ Arranges the children of the frame (typically only one) in
        a vertical box sizer.

        """
        sizer = wx.BoxSizer(wx.VERTICAL)
        for child in self.parent.children:
            flags = compute_sizer_flags(child)
            sizer.AddF(child.toolkit_impl.widget, flags)
        self.widget.SetSizer(sizer)
        sizer.Layout()

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

    def parent_title_changed(self, title):
        """ The change handler for the 'title' attribute. Not meant for 
        public consumption.

        """
        self.set_title(title)
    
    def parent_modality_changed(self, modality):
        """ The change handler for the 'modality' attribute. Not meant 
        for public consumption.

        """
        self.set_modality(modality)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
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
            if modality in (Modality.APPLICATION_MODAL, Modality.WINDOW_MODAL):
                self.widget.MakeModal(True)
            else:
                self.widget.MakeModal(False)

