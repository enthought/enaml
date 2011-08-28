import wx

from traits.api import implements, Str, Enum

from .wx_panel import WXPanel

from ..i_window import IWindow

from ...enums import Modality


class WXWindow(WXPanel):

    implements(IWindow)

    #===========================================================================
    # IWindow interface
    #===========================================================================
    title= Str

    modality = Enum(*Modality.values())

    def show(self):
        if self.needs_layout:
            self.layout(None)
        else:
            if self.needs_container_layout:
                if self.widget:
                    self.widget.Hide()
                self.layout_container()
        self.widget.Show()

    def hide(self):
        if self.widget:
            self.widget.Hide()

    #===========================================================================
    # Implementation
    #===========================================================================

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_widget(self):
        self.widget = wx.Frame(self.parent_widget())

    def init_attributes(self):
        self.set_title(self.title)
        self.set_modality(self.modality)
    
    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    def _title_changed(self, title):
        self.set_title(title)
    
    def _modality_changed(self, modality):
        self.set_modality(modality)

    #---------------------------------------------------------------------------
    # Widget update
    #---------------------------------------------------------------------------
    def set_title(self, title):
        self.widget.SetTitle(title)
    
    def set_modality(self, modality):
        # The wx frame cannot distinguish between application and
        # window modal (AFAIK). I think we need a wxDialog for that.
        if modality in (Modality.APPLICATION_MODAL, Modality.WINDOW_MODAL):
            self.widget.MakeModal(True)
        else:
            self.widget.MakeModal(False)

