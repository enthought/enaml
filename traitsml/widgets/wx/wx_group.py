import wx

from traits.api import implements, Enum

from .wx_container import WXContainer

from ..i_group import IGroup

from ...enums import Direction


class WXGroup(WXContainer):

    implements(IGroup)

    #===========================================================================
    # IGroup interface
    #===========================================================================
    direction = Enum(*Direction.values())

    #===========================================================================
    # Implementation
    #===========================================================================

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_sizer(self):
        self.widget = self.make_sizer(self.direction)
        
    def layout_children(self):
        super(WXGroup, self).layout_children()
        sizer = self.widget
        if self.is_reverse_direction(self.direction):
            children = reversed(list(self.children()))
        else:
            children = self.children()
        self.fill_sizer(sizer, children)
        sizer.Layout()

    def init_attributes(self):
        pass

    def init_meta_handlers(self):
        pass
    
    #---------------------------------------------------------------------------
    # Sizer logic
    #---------------------------------------------------------------------------
    def make_sizer(self, direction):
        dirs = (Direction.LEFT_TO_RIGHT, Direction.RIGHT_TO_LEFT)
        if direction in dirs:
            sizer = wx.BoxSizer(wx.HORIZONTAL)
        else:
            sizer = wx.BoxSizer(wx.VERTICAL)
        return sizer

    def fill_sizer(self, sizer, children):
        # XXX update this logic to use hints from child handlers.
        for child in children:
            #weight = child.default_layout_weight()
            #expand = child.default_layout_expand()
            #sizer.Add(child.widget, weight, expand)
            sizer.Add(child.widget, 1, wx.EXPAND)
        
    def is_reverse_direction(self, direction):
        dirs = (Direction.RIGHT_TO_LEFT, Direction.BOTTOM_TO_TOP)
        return direction in dirs

    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    def _direction_changed(self, direction):
        old_sizer = self.widget
        new_sizer = self.make_sizer(direction)
        parent_sizer = self.parent_sizer()

        if self.is_reverse_direction(direction):
            children = reversed(list(self.children()))
        else:
            children = self.children()
        self.fill_sizer(new_sizer, children)
        
        # XXX This is a bit of hack. We should just be able to grab
        # the parent sizer and do a .Replace() on it. But that segfaults
        # in OSX 10.6 (I haven't checked other platforms). So the 
        # workaround is manually remove the old and insert the new in
        # proper place.
        if parent_sizer:
            sizer_item = parent_sizer.GetItem(old_sizer)
            if sizer_item:
                idx = parent_sizer.GetChildren().index(sizer_item)
                parent_sizer.Remove(old_sizer)
                parent_sizer.Insert(idx, new_sizer, 1, wx.EXPAND)
                self.widget = new_sizer
                parent_sizer.Layout()

