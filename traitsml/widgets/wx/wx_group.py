import wx

from traits.api import implements, Enum

from .wx_container import WXContainer

from ..i_group import IGroup

from ...enums import Direction


class WXGroup(WXContainer):
    """ A wxPython implementation of IGroup.

    The WXGroup uses a wxBoxSizer to arrange its child components.

    See Also
    --------
    IGroup

    """
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
    def create_widget(self):
        """ Creates the underlying sizer for the group. 

        This is called by the 'layout' method and is not meant for public
        consumption.

        """
        self.widget = self.make_sizer(self.direction)
        
    def layout_children(self):
        """ Adds the children of this container to the sizer.
        
        This is called by the 'layout' method and is not meant for 
        public consumption.

        """
        for child in self.children():
            child.layout(self)
        sizer = self.widget
        if self.is_reverse_direction(self.direction):
            children = reversed(list(self.children()))
        else:
            children = self.children()
        self.fill_sizer(sizer, children)
        sizer.Layout()

    def init_attributes(self):
        """ Initializes the attributes of the sizer.

        This is called by the 'layout' method and is not meant for 
        public consumption.

        """
        pass

    def init_meta_handlers(self):
        """ Initializes the meta handlers of the sizer.

        This is called by the 'layout' method and is not meant for 
        public consumption.

        """
        pass
    
    def do_add_child(self, child):
        """ Adds a new child to the sizer.

        This is called by the 'add_child' method and is not meant for 
        public consumption.

        """
        # XXX not yet supported
        pass

    def do_remove_child(self, child):
        """ Removes a child from the sizer.

        This is called by the 'remove_child' method and is not meant for 
        public consumption.

        """
        # XXX not yet supported
        pass
    
    def do_replace_child(self, child, other_child, idx):
        """ Replaces a child in the sizer.

        This is called by the 'replace_child' method and is not meant for 
        public consumption.

        """
        # XXX not yet supported
        pass
    
    #---------------------------------------------------------------------------
    # Sizer logic
    #---------------------------------------------------------------------------
    def make_sizer(self, direction):
        """ Creates a wxBoxSizer for the given direction value. Not
        meant for public consumption.

        """
        dirs = (Direction.LEFT_TO_RIGHT, Direction.RIGHT_TO_LEFT)
        if direction in dirs:
            sizer = wx.BoxSizer(wx.HORIZONTAL)
        else:
            sizer = wx.BoxSizer(wx.VERTICAL)
        return sizer

    def fill_sizer(self, sizer, children):
        """ Fills the given sizer with the iterable of children. Not
        meant for public consumption.

        """
        for child in children:
            sizer.AddF(child.widget, child.default_sizer_flags())
        
    def is_reverse_direction(self, direction):
        """ Returns True or False depending on if the given direction
        is reversed from normal. Not meant for public consumption.

        """
        dirs = (Direction.RIGHT_TO_LEFT, Direction.BOTTOM_TO_TOP)
        return direction in dirs

    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    def _direction_changed(self, direction):
        """ The change handle for the 'direction' attribute. Not meant
        for public consumption.

        """
        # XXX This whole method is a bit of a hack. We probably want
        # an api on our parent where we can request a relayout.
        
        new_sizer = self.make_sizer(direction)
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
        parent_sizer = self.parent_sizer()
        if parent_sizer:
            old_sizer = self.widget
            sizer_item = parent_sizer.GetItem(old_sizer)
            if sizer_item:
                idx = parent_sizer.GetChildren().index(sizer_item)
                parent_sizer.Remove(old_sizer)
                parent_sizer.InsertF(idx, new_sizer, self.default_sizer_flags())
                self.widget = new_sizer
                parent_sizer.Layout()

