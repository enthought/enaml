#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_container import WXContainer

from ..scroll_area import AbstractTkScrollArea


# As mentioned in the notes of the docstring for WXScrollArea, we
# don't support the 'always_on' policy of the scrollbars. Since
# we only have to support 'off' or 'auto' it's easiest to use this
# mapping to convert straight from policy values into a respective
# scroll rate. A rate of Zero causes wx not to show the scroll bar.
# A positive rate indicates to scroll that many pixels per event.
# We set the rate to 1 to have smooth scrolling. Wx doesn't make a
# distinction between scroll events caused by the mouse or scrollbar
# and those caused by clicking the scroll buttons (ala qt), and thus
# this rate applies the same to all of those events. Since we expect
# that clicking on a scroll button happens much more infrequently 
# than scrolling by dragging the scroll bar, we opt for a lower rate
# in order to get smooth drag scrolling and sacrifice some usability
# on the scroll buttons.
SCROLLBAR_POLICY_MAP = {
     'as_needed': 1,
     'always_off': 0,
     'always_on': 1,
}


class ScrollSizer(wx.PySizer):
    """ A custom wx Sizer for use in the WXScrollArea. It manages the
    necessary resizing of the child container when the scroll area
    is resized.

    """
    def __init__(self, child):
        """ Initializes a ScrollSizer

        Parameters
        ----------
        child :
            The child container this size is managing.
        
        """
        super(ScrollSizer, self).__init__()
        self.child = child

    def CalcMin(self):
        """ Returns the minimum size of the child this sizer is managing.

        """
        return self.child.min_size()
    
    def RecalcSizes(self):
        """ Resizes the child to fit the available space of the scroll
        area.

        """
        # XXX this probably wont do the right thing if the child
        # is not a container and shouldn't be resized.
        self.child.resize(*self.GetSizeTuple())


class WXScrollArea(WXContainer, AbstractTkScrollArea):
    """ Wx implementation of the ScrollArea Container.

    ..Note: The 'always_on' scrollbar policy is not supported on wx. Wx
        *does* allow the scollbars to be always show, but said window 
        style applies to *both* horizontal and vertical directions, and
        it must be applied at widget creation time. It does not reliably
        toggle on/off dynamically after the widget has been created. As
        it's not reliable, we simple support that mode on wx. Should it
        become a highly desired feature, this decision can be revisited.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QScrollAreacontrol.

        """
        style = wx.HSCROLL | wx.VSCROLL | wx.BORDER_SIMPLE 
        self.widget = wx.ScrolledWindow(self.parent_widget(), style=style)
    
    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(WXScrollArea, self).initialize()
        shell = self.shell_obj
        self._set_horiz_policy(shell.horizontal_scrollbar_policy)
        self._set_vert_policy(shell.vertical_scrollbar_policy)
        self._update_children()

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
        of the scroll area. Overridden from the parent class to return
        a reasonable value for a Scroll Area.

        """
        # Trying to have wx compute a decent size hint is probably
        # the most painful thing i've experienced in programming. It's 
        # just not worth the effort. For now, just return the default 
        # size hint used by QAbstractScrollArea.
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
        # Setup a custom sizer for the child widget so that it receives
        # resize events at the appropriate times. There doesn't seem to
        # be any other way to make this work in wx.

        # XXX at the moment, we don't really handle children updates
        # properly. This can be done, but we'll need some contracts
        # in place about the safety of calling a re-setup on a child
        # when its added or removed from a component dynamically.
        # For now, we just assume that there is one child, and
        # that it never changes.
        shell = self.shell_obj
        if len(shell.children) == 0:
            pass
        else:
            sizer = ScrollSizer(shell.children[0])
            self.widget.SetSizer(sizer)
            self.widget.Refresh()

