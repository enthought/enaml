#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from traits.api import implements

from .wx_container import WXContainer
from .styling import compute_sizer_flags

from ..group import IGroupImpl

from ...enums import Direction

            
class WXGroup(WXContainer):
    """ A wxPython implementation of IGroup.

    The WXGroup uses a wxBoxSizer to arrange its child components.

    See Also
    --------
    IGroup

    """
    implements(IGroupImpl)

    #---------------------------------------------------------------------------
    # IGroupImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying sizer for the group. 

        """
        self.widget = self.make_sizer(self.parent.direction)
        
    def initialize_widget(self):
        """ Nothing to initialize on a group.

        """
        pass

    def layout_child_widgets(self):
        """ Adds the children of this container to the sizer.

        """
        # XXX - the wx box model is terrible and we have not way of 
        # specifying inter-item spacing in a group while also specifying
        # an independent border. So, if we get a spacing value, we just
        # punt and add it to the border width and set the border to ALL.
        spacing = self.parent.style.get_property('spacing')
        if isinstance(spacing, int) and spacing >= 0:
            pass
        else:
            spacing = False
        sizer = self.widget
        for child in self.parent.children:
            flags = compute_sizer_flags(child.style)
            if spacing:
                border = flags.GetBorderInPixels()
                border += spacing
                flags.Border(wx.ALL, border)
            sizer.AddF(child.toolkit_impl.widget, flags)
        sizer.Layout()

    def parent_direction_changed(self, direction):
        """ The change handler for the 'direction' attribute on the 
        parent.

        """
        pass
    
    #---------------------------------------------------------------------------
    # Implementation
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
        
    def is_reverse_direction(self, direction):
        """ Returns True or False depending on if the given direction
        is reversed from normal. Not meant for public consumption.

        """
        dirs = (Direction.RIGHT_TO_LEFT, Direction.BOTTOM_TO_TOP)
        return direction in dirs

