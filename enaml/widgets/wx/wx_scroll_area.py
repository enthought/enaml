#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_container import WXContainer

from ..scroll_area import AbstractTkScrollArea


SCROLLBAR_POLICY_MAP = dict(
     as_needed=1,
     always_off=0,
     always_on=1,
)


class ScrollSizer(wx.PySizer):

    def __init__(self, child):
        super(ScrollSizer, self).__init__()
        self.child = child
        self.min_size = None
        
    def CalcMin(self):
        if self.min_size is None:
            self.min_size = wx.Size(*self.child.layout.calc_min_size())
        return self.min_size
    
    def RecalcSizes(self):
        self.child.resize(*self.GetSizeTuple())


class WXScrollArea(WXContainer, AbstractTkScrollArea):
    """ Wx implementation of the ScrollArea Container.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QScrollAreacontrol.

        """
        self.widget = wx.ScrolledWindow(self.parent_widget())
    
    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(WXScrollArea, self).initialize()
        shell = self.shell_obj
        self._set_horiz_policy(shell.horizontal_scrollbar_policy)
        self._set_vert_policy(shell.vertical_scrollbar_policy)
        child = self.shell_obj.children[0]
        sizer = ScrollSizer(child)
        self.widget.SetSizer(sizer)
        
    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_horizontal_scrollbar_policy_changed(self, policy):
        """ The change handler for the 'horizontal_scrollbar_policy'
        attribute of the shell object.

        """
        self._set_horiz_policy(policy)

    def shell_vertical_scrollbar_policy_changed(self, policy):
        """ The change handler for the 'vertical_scrollbar_policy'
        attribute of the shell object.

        """
        self._set_vert_policy(policy)

    def shell_children_changed(self, children):
        """ The change handler for the children of the shell object.

        """
        self._update_children()

    def shell_children_items_changed(self, event):
        """ The change handler for the children items event of the
        shell object.

        """
        # XXX this won't work because traits does not properly hook
        # up items event listeners via calls to .add_trait_listener
        # which is how this object has been hooked up.
        self._update_children()
    
    def size_hint(self):
        """ Returns a (width, height) tuple of integers for the size hint
        of the scroll area.

        """
        # Trying to have wx compute a decent size hint is probably
        # the most painful thing i've experienced in programming. It's 
        # just not worth the effort. For now, just return the default 
        # used by QAbstractScrollArea
        return (256, 192)

    #--------------------------------------------------------------------------
    # Widget Update
    #--------------------------------------------------------------------------
    def _set_horiz_policy(self, policy):
        """ Set the horizontal scrollbar policy of the widget.

        """
        horiz = SCROLLBAR_POLICY_MAP[policy]
        vert = SCROLLBAR_POLICY_MAP[self.shell_obj.vertical_scrollbar_policy]
        self.widget.SetScrollRate(horiz, vert)

    def _set_vert_policy(self, policy):
        """ Set the vertical scrollbar policy of the widget.

        """
        horiz = SCROLLBAR_POLICY_MAP[self.shell_obj.horizontal_scrollbar_policy]
        vert = SCROLLBAR_POLICY_MAP[policy]
        self.widget.SetScrollRate(horiz, vert)
   
    def _update_children(self):
        """ Update the QScrollArea's children with the current children.

        """
        return
        # shell = self.shell_obj
        # if len(shell.children) == 0:
        #     self.widget.setWidget(None)
        # else:
        #     self.widget.setWidget(shell.children[0].toolkit_widget)

