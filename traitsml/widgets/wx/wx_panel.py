import wx

from traits.api import implements, Instance, Bool

from .wx_component import WXComponent
from .wx_container import WXContainer

from ..i_panel import IPanel


class WXPanel(WXComponent):

    implements(IPanel)

    #===========================================================================
    # IPanel interface
    #===========================================================================
    def layout(self, parent):
        self.set_parent(parent)
        self.create_widget()
        self.layout_container()
        self.init_attributes()
        self.init_meta_handlers()
        self.needs_layout = False

    def set_container(self, container):
        self.container = container
        self.needs_container_layout = True

    def get_container(self):
        return self.container

    #===========================================================================
    # Implementation
    #===========================================================================
    # The container of child widgets
    container = Instance(WXContainer)

    # Whether the window needs to be layed out
    needs_layout = Bool(True)

    # Whether we need to re-layout the container before showing.
    needs_container_layout = Bool(True)

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_widget(self):
        self.widget = wx.Panel(self.parent_widget())

    def layout_container(self):
        container = self.container
        if container is not None:
            for child_widget in self.widget.GetChildren():
                if child_widget:
                    child_widget.Destroy()
            container.layout(self)
            self.widget.SetSizer(container.widget, True)
            self.widget.Layout()
        self.needs_container_layout = False

    def init_attributes(self):
        pass
    
    def init_meta_handlers(self):
        pass

    