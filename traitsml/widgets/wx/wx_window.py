import wx

from traits.api import implements, Str, Enum, Instance, Bool, Property

from .wx_component import WXComponent
from .wx_container import WXContainer

from ..i_window import IWindow

from ...enums import Modality


class WXWindow(WXComponent):

    implements(IWindow)

    #---------------------------------------------------------------------------
    # IWindow interface
    #---------------------------------------------------------------------------
    title= Str

    modality = Enum(*Modality.values())

    def layout(self, parent=None):
        self.create_window(parent)
        self.layout_container()
        self.init_attributes()
        self.init_meta_handlers()
        self.needs_layout = False

    def set_container(self, container):
        self.container = container
        self.needs_container_layout = True

    def get_container(self):
        return self.container

    def show(self):
        if self.needs_layout:
            self.layout()
        else:
            if self.needs_container_layout:
                if self.widget is not None:
                    self.widget.Hide()
                self.layout_container()
        self.widget.Show()

    def hide(self):
        if self.widget is not None:
            self.widget.Hide()

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    
    # The container of child widgets
    container = Instance(WXContainer)

    # Whether the window needs to be layed out
    needs_layout = Bool(True)

    # Whether we need to re-layout the container before showing.
    needs_container_layout = Bool(True)

    # Whether or not the window is visible on the screen.
    is_visible = Property

    def create_window(self, parent=None):
        parent_widget = parent.widget if parent is not None else None
        self.widget = wx.Frame(parent_widget)

    def layout_container(self):
        container = self.container
        if container is not None:
            for child_widget in self.widget.GetChildren():
                child_widget.Destroy()
            container.layout(self)
            self.widget.Layout()
        self.needs_container_layout = False

    def init_attributes(self):
        self._title_changed(self.title)
        self._modality_changed(self.modality)
    
    def init_meta_handlers(self):
        pass

    def _get_is_visible(self):
        return self.widget is not None and self.widget.IsShown()

    def _title_changed(self, title):
        self.widget.SetTitle(title)
    
    def _modality_changed(self, modality):
        # The wx frame cannot distinguish between application and
        # window modal (AFAIK). I think we need a wxDialog for that.
        if modality in (Modality.APPLICATION_MODAL, Modality.WINDOW_MODAL):
            self.widget.MakeModal(True)
        else:
            self.widget.MakeModal(False)

