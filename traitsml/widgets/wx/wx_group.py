import wx

from traits.api import implements, Enum, Property, Bool

from .wx_container import WXContainer

from ..i_group import IGroup

from ...enums import Direction


class WXGroup(WXContainer):

    implements(IGroup)

    #---------------------------------------------------------------------------
    # IGroup interface
    #---------------------------------------------------------------------------
    direction = Enum(*Direction.values())

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    is_reverse_layout = Property(Bool)

    def create_panel(self, parent):
        self.widget = wx.Panel(parent.widget)

    def create_sizer(self):
        dirs = (Direction.LEFT_TO_RIGHT, Direction.RIGHT_TO_LEFT)
        if self.direction in dirs:
            sizer = wx.BoxSizer(wx.HORIZONTAL)
        else:
            sizer = wx.BoxSizer(wx.VERTICAL)
        self.widget.SetSizer(sizer, True)
        self.sizer = sizer
        
    def layout_children(self):
        super(WXGroup, self).layout_children()
        sizer = self.sizer
        for child in self.children():
            sizer.Add(child.widget, 1)
        self.widget.Layout()

    def init_attributes(self):
        pass

    def init_meta_handlers(self):
        pass

    def _get_is_reverse_layout(self):
        dirs = (Direction.RIGHT_TO_LEFT, Direction.BOTTOM_TO_TOP)
        return self.direction in dirs

    def _direction_changed(self, direction):
        self.create_sizer()
        sizer = self.sizer
        if self.is_reverse_layout:
            children = reversed(list(self.children()))
        else:
            children = self.children()
        for child in children:
            sizer.Add(child.widget, 1)
        self.widget.Layout()

