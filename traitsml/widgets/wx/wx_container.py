import wx

from traits.api import implements, Instance, Bool

from .wx_component import WXComponent

from ..i_container import IContainer
from ..mixins.container_mixin import ContainerMixin


class WXContainer(WXComponent, ContainerMixin):
    
    implements(IContainer)

    #---------------------------------------------------------------------------
    # IContainer interface
    #---------------------------------------------------------------------------

    # The IContainer interface is provided by the ContainerMixin

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    
    # The wx sizer in user for this container
    sizer = Instance(wx.Sizer)

    # A flag to tell whether or not we've been layed out proper
    # and we can therefore expect our children to have widgets
    layed_out = Bool(False)

    # For all of these child methods, if we haven't been layed out
    # then we don't need to do anything as it will be handled when
    # layout() is called. Otherwise, we'll need to layout the child
    # before manipulating it.
    def do_add_child(self, child):
        if self.layed_out:
            child.layout(self)
            if child.widget:
                self.sizer.Add(child.widget)
                self.widget.Layout()

    def do_remove_child(self, child):
        if self.layed_out:
            if child.widget:
                child.widget.Destroy()
                self.Layout()

    def do_replace_child(self, child, other_child, idx):
        if self.layed_out:
            if child.widget and other_child.widget:
                if self.sizer.Replace(child.widget, other_child.widget):
                    child.widget.Destroy()
                    self.Layout()

    def layout(self, parent):
        self.create_panel(parent)
        self.create_sizer()
        self.layout_children()
        self.init_attributes()
        self.init_meta_handlers()
        self.layed_out = True

    def create_panel(self, parent):
        raise NotImplementedError

    def create_sizer(self):
        raise NotImplementedError

    def layout_children(self):
        for child in self.children():
            child.layout(self)

    def init_attributes(self):
        raise NotImplementedError

    def init_meta_handlers(self):
        raise NotImplementedError

