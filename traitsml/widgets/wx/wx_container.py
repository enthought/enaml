from traits.api import implements, Bool

from .wx_component import WXComponent

from ..i_container import IContainer
from ..mixins.container_mixin import ContainerMixin


class WXContainer(WXComponent, ContainerMixin):

    implements(IContainer)

    #===========================================================================
    # IContainer interface
    #===========================================================================
    def layout(self, parent):
        self.set_parent(parent)
        self.create_sizer()
        self.layout_children()
        self.init_attributes()
        self.init_meta_handlers()
        self.layed_out = True

    # The rest of the IContainer interface is provided by the ContainerMixin

    #===========================================================================
    # Implementation
    #===========================================================================
    # A flag to tell whether or not we've been layed out proper
    # and we can therefore expect our children to have widgets
    layed_out = Bool(False)

    #---------------------------------------------------------------------------
    # Overriden parent class methods
    #---------------------------------------------------------------------------
    def do_add_child(self, child):
        if self.layed_out:
            child.layout(self)
            item = child.widget
            if item:
                sizer = self.widget
                sizer.Add(item)
                sizer.Layout()

    def do_remove_child(self, child, idx):
        if self.layed_out:
            item = child.widget
            if item:
                sizer = self.widget
                if sizer.Remove(item):
                    if item:
                        item.Destroy()
                    sizer.Layout()

    def do_replace_child(self, child, other_child, idx):
        if self.layed_out:
            item = child.widget
            if item:
                other_child.layout(self)
                other_item = other_child.widget
                sizer = self.widget
                if sizer.Replace(item, other_item):
                    if item:
                        item.destroy()
                    sizer.Layout()
    
    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_sizer(self):
        raise NotImplementedError

    def layout_children(self):
        for child in self.children():
            child.layout(self)

    def init_attributes(self):
        raise NotImplementedError

    def init_meta_handlers(self):
        raise NotImplementedError

