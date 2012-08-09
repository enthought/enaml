#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_constraints_widget import WxConstraintsWidget


# The 'always_on' scroll policy is not supported on wx, because it
# requires setting a window style flag which does not dynamically 
# toggle in a reliable fashion. Since we only support 'off' or 'auto'
# it's easiest to use this mapping to convert straight from policy 
# values into a respective scroll rate. A rate of Zero causes wx not 
# to show the scroll bar. A positive rate indicates to scroll that many
# pixels per event. We set the rate to 1 to have smooth scrolling. Wx 
# doesn't make a distinction between scroll events caused by the mouse 
# or scrollbar and those caused by clicking the scroll buttons (ala qt), 
# and thus this rate applies the same to all of those events. Since we 
# expect that clicking on a scroll button happens much more infrequently 
# than scrolling by dragging the scroll bar, we opt for a lower rate
# in order to get smooth drag scrolling and sacrifice some usability
# on the scroll buttons.
SCROLLBAR_MAP = {
    'as_needed': 1,
    'always_off': 0,
    'always_on': 1,
}


class wxScrollAreaSizer(wx.PySizer):
    """ A custom wxSizer for use in the WxScrollArea. 

    This sizer expands its child to fit the allowable space, regardless
    of the settings the child widget. However, the minimum size of the
    child is respected. There can only be one widget managed by this
    sizer at time. Old widgets will be removed automatically, but they
    will not be destroyed.

    """
    #: The widget which is manipulated by the sizer.
    _widget = None

    def Add(self, widget):
        """ Adds the given child widget to the sizer.

        This will remove any previous widget set in the sizer, but it
        will not be destroyed.

        Parameters
        ----------
        widget : wxWindow
            The wx window widget to manage with this sizer.

        """
        self.Clear(deleteWindows=False)
        self._widget = widget
        if widget is not None:
            res = super(wxScrollAreaSizer, self).Add(widget)
            # The call to Layout is required, because it's not done
            # automatically by wx and the new item wouldn't properly
            # lay out otherwise.
            self.Layout()
            return res

    def CalcMin(self):
        """ Returns the minimum size for the area owned by the sizer.

        Returns
        -------
        result : wxSize
            The wx size representing the minimum area required by the
            sizer.

        """
        widget = self._widget 
        if widget is not None:
            res = widget.GetEffectiveMinSize()
            # There is a two pixel error on the min size for when scroll
            # bars show up. We correct for that here.
            res.width -= 2
            res.height -= 2
        else:
            res = wx.Size(-1, -1)
        return res
    
    def RecalcSizes(self):
        """ Resizes the child to fit in the available space.

        """
        widget = self._widget
        if widget is not None:
            widget.SetSize(self.GetSize())


class wxScrollArea(wx.ScrolledWindow):
    """ A subclass of wx.ScrolledWindow which returns a sensible best
    size.

    """
    #: The internal best size. The same as QAbstractScrollArea.
    _best_size = wx.Size(256, 192)

    def GetBestSize(self):
        """ An overridden parent class method which returns a sensible
        best size.

        The default wx implementation returns a best size of (16, 16)
        on Windows; far too small to be useful. So, we just adopt the
        size hint of (256, 192) used in Qt's QAbstractScrollArea.

        """
        return self._best_size


class WxScrollArea(WxConstraintsWidget):
    """ A Wx implementation of an Enaml ScrollArea.

    """
    #: Storage for the horizontal scroll policy
    _h_scroll = 'as_needed'

    #: Storage for the vertical scroll policy
    _v_scroll = 'as_needed'

    def create_widget(self, parent, tree):
        """ Create the underlying wxScrolledWindow widget.

        """
        style = wx.HSCROLL | wx.VSCROLL | wx.BORDER_SIMPLE 
        return wxScrollArea(parent, style=style)

    def create(self, tree):
        """ Create and initialize the scroll area widget.

        """
        super(WxScrollArea, self).create(tree)
        self.set_horizontal_scrollbar(tree['horizontal_scrollbar'])
        self.set_vertical_scrollbar(tree['vertical_scrollbar'])

    def post_create(self):
        """ Handle post creation for the scroll area.

        This methods adds the first child as the scrolled widget.
        Specifying more than one child of a scroll area will result
        in undefined behavior.

        """
        children = self.children()
        if children:
            sizer = wxScrollAreaSizer()
            sizer.Add(children[0].widget())
            self.widget().SetSizer(sizer)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_horizontal_scrollbar(self, content):
        """ Handle the 'set_horizontal_scrollbar' action from the Enaml
        widget.

        """
        policy = content['horizontal_scrollbar']
        self.set_horizontal_scrollbar(policy)

    def on_action_set_vertical_scrollbar(self, content):
        """ Handle the 'set_vertical_scrollbar' action from the Enaml
        widget.

        """
        policy = content['vertical_scrollbar']
        self.set_vertical_scrollbar(policy)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_horizontal_scrollbar(self, policy):
        """ Set the horizontal scrollbar policy of the widget.

        """
        self._h_scroll = policy
        horiz = SCROLLBAR_MAP[policy]
        vert = SCROLLBAR_MAP[self._v_scroll]
        self.widget().SetScrollRate(horiz, vert)
        
    def set_vertical_scrollbar(self, policy):
        """ Set the vertical scrollbar policy of the widget.

        """
        self._v_scroll = policy
        horiz = SCROLLBAR_MAP[self._h_scroll]
        vert = SCROLLBAR_MAP[policy]
        self.widget().SetScrollRate(horiz, vert)

