import wx

from traits.api import implements

from .wx_component import WXComponent

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
        self.widget = wx.Frame(None)#self.parent_widget())
    
    def initialize_widget(self):
        self.set_title(self.parent.title)
        self.set_modality(self.parent.modality)

    def layout_child_widgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        for child in self.child_widgets():
            sizer.Add(child, 1, wx.EXPAND)
        self.widget.SetSizer(sizer)

    def show(self):
        """ Displays the window to the screen, laying out if necessary.
        
        Call this method to display the window to the screen. If layout 
        is necessary, this method will lay out the window with no parent. 
        If supplying a parent is necessary, manually call the 'layout' 
        method with the parent before calling 'show'.
        
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
    # Widget update
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

