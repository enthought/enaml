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


class WXScrollAreaSizer(wx.PySizer):
    """ A custom wx Sizer for use in the WXScrollArea. This sizer expands
    its child to fit the allowable space, regardless of the settings on
    the child settings.

    There can only be one component in this sizer at a time and it 
    should be added via the .Add(...) method. Old items will be removed 
    automatically (but not destroyed).

    """
    #: The child component which is manipulated by the sizer.
    _child = None

    def Add(self, component):
        """ Adds the given child component to the sizer, removing the 
        old widget if present. The old widget is not destroyed.

        """
        self.Clear(deleteWindows=False)
        self._child = component
        if component is not None:
            child_widget = component.toolkit_widget
            res = super(WXScrollAreaSizer, self).Add(child_widget)
            # We need to call Layout here, because it's not done
            # automatically by wx and otherwise the new item won't
            # be layed out properly.
            self.Layout()
            return res

    def CalcMin(self):
        """ Returns the minimum size for the children this sizer is 
        managing. Since the size of the Dialog is managed externally,
        this always returns (-1, -1).

        """
        component = self._child
        if component is not None:
            res = component.min_size()
        else:
            res = (-1, -1)
        return res
    
    def RecalcSizes(self):
        """ Resizes the child to fit the available space of the scroll
        area.

        """
        component = self._child
        if component is not None:
            component.resize(*self.GetSizeTuple())


class WXScrollArea(WXContainer, AbstractTkScrollArea):
    """ Wx implementation of the ScrollArea Container.

    ..Note: The 'always_on' scrollbar policy is not supported on wx. Wx
        *does* allow the scollbars to be always shown, but said window 
        style applies to *both* horizontal and vertical directions, and
        it must be applied at widget creation time. It does not reliably
        toggle on/off dynamically after the widget has been created. As
        it's not reliable, we simply don't support it on wx. Should it
        become a highly desired feature, this decision can be revisited.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QScrollAreacontrol.

        """
        style = wx.HSCROLL | wx.VSCROLL | wx.BORDER_SIMPLE 
        self.widget = wx.ScrolledWindow(parent, style=style)
        self.widget.SetSizer(WXScrollAreaSizer())

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(WXScrollArea, self).initialize()
        shell = self.shell_obj
        self.set_horizontal_policy(shell.horizontal_scrollbar_policy)
        self.set_vertical_policy(shell.vertical_scrollbar_policy)
        self.update_scrolled_component()

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_horizontal_scrollbar_policy_changed(self, policy):
        """ The change handler for the 'horizontal_scrollbar_policy'
        attribute of the shell object.

        """
        self.set_horizontal_policy(policy)

    def shell_vertical_scrollbar_policy_changed(self, policy):
        """ The change handler for the 'vertical_scrollbar_policy'
        attribute of the shell object.

        """
        self.set_vertical_policy(policy)

    def shell_scrolled_component_changed(self, component):
        """ The change handler for the 'layout_children' attribute of 
        the shell object.

        """
        self.update_scrolled_component()
    
    def size_hint(self):
        """ Returns a (width, height) tuple of integers for the size hint
        of the scroll area. Overridden from the parent class to return
        a reasonable value for a Scroll Area.

        """
        # Trying to have wx compute a decent size hint is probably
        # the most painful thing i've experienced in programming. It's 
        # just not worth the effort. For now, we try to compute from the
        # min size of the sizer, and if that fails just return the size 
        # hint used by QAbstractScrollArea.
        res = self.widget.GetSizer().CalcMin()
        if res == (-1, -1):
            res = (256, 192)
        return res

    #--------------------------------------------------------------------------
    # Widget Update
    #--------------------------------------------------------------------------
    def set_horizontal_policy(self, policy):
        """ Set the horizontal scrollbar policy of the widget.

        """
        horiz = SCROLLBAR_POLICY_MAP[policy]
        vert = SCROLLBAR_POLICY_MAP[self.shell_obj.vertical_scrollbar_policy]
        self.widget.SetScrollRate(horiz, vert)

    def set_vertical_policy(self, policy):
        """ Set the vertical scrollbar policy of the widget.

        """
        horiz = SCROLLBAR_POLICY_MAP[self.shell_obj.horizontal_scrollbar_policy]
        vert = SCROLLBAR_POLICY_MAP[policy]
        self.widget.SetScrollRate(horiz, vert)
   
    def update_scrolled_component(self):
        """ Update the QScrollArea's children with the current children.

        """
        sizer = self.widget.GetSizer()
        sizer.Add(self.shell_obj.scrolled_component)

