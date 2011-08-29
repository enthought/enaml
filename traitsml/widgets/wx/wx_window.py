import wx

from traits.api import implements, Str, Enum

from .wx_panel import WXPanel

from ..i_window import IWindow

from ...enums import Modality


class WXWindow(WXPanel):
    """ A wxPython implementation of IWindow.

    WXWindow uses a wx.Frame to create a simple top level window which
    contains other child widgets and layouts.

    See Also
    --------
    IWindow

    """
    implements(IWindow)

    #===========================================================================
    # IWindow interface
    #===========================================================================
    title= Str

    modality = Enum(*Modality.values())

    def show(self):
        """ Displays the window to the screen, laying out if necessary.
        
        Call this method to display the window to the screen. If layout 
        is necessary, this method will lay out the window with no parent. 
        If supplying a parent is necessary, manually call the 'layout' 
        method with the parent before calling 'show'.
        
        """
        if self.needs_layout:
            self.layout(None)
        else:
            if self.needs_container_layout:
                if self.widget:
                    self.widget.Hide()
                self.layout_container()
        self.widget.Show()

    def hide(self):
        """ Hide the window from the screen.

        """
        if self.widget:
            self.widget.Hide()

    #===========================================================================
    # Implementation
    #===========================================================================

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying wx.Frame control.

        This is is called by the 'layout' method and is not meant for
        public consumption.

        """
        self.widget = wx.Frame(self.parent_widget())

    def init_attributes(self):
        """ Initializes the attributes of the frame.

        This is is called by the 'layout' method and is not meant for
        public consumption.

        """
        self.set_title(self.title)
        self.set_modality(self.modality)
    
    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    def _title_changed(self, title):
        """ The change handler for the 'title' attribute. Not meant for 
        public consumption.

        """
        self.set_title(title)
    
    def _modality_changed(self, modality):
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
        self.widget.SetTitle(title)
    
    def set_modality(self, modality):
        """ Sets the modality of the frame. Not meant for public
        consumption.

        """
        # The wx frame cannot distinguish between application and
        # window modal (AFAIK). I think we need a wxDialog for that.
        if modality in (Modality.APPLICATION_MODAL, Modality.WINDOW_MODAL):
            self.widget.MakeModal(True)
        else:
            self.widget.MakeModal(False)

