#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_constraints_widget import WxConstraintsWidget
from .wx_single_widget_sizer import wxSingleWidgetSizer


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


class wxScrollAreaSizer(wxSingleWidgetSizer):
    """ A wxSingleWidgetSizer subclass which makes adjusts the min
    size to account for a 2 pixel error in Wx.

    """
    def CalcMin(self):
        """ Returns the minimum size for the area owned by the sizer.

        Returns
        -------
        result : wxSize
            The wx size representing the minimum area required by the
            sizer.

        """
        # The effective min size computation is correct, but the wx
        # scrolled window interprets it with an error of 2px. That
        # is we need to make wx think that the min size is 2px smaller
        # than it actually is so that scroll bars should and hide at
        # the appropriate sizes.
        res = super(wxScrollAreaSizer, self).CalcMin()
        if res.IsFullySpecified():
            res.width -= 2
            res.height -= 2
        return res


class wxScrollArea(wx.ScrolledWindow):
    """ A custom wx.ScrolledWindow which is suits Enaml's use case.

    """
    #: The internal best size. The same as QAbstractScrollArea.
    _best_size = wx.Size(256, 192)

    def __init__(self, *args, **kwargs):
        """ Initialize a wxScrollArea.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a wxScrolledWindow.

        """
        super(wxScrollArea, self).__init__(*args, **kwargs)
        self._scroll_widget = None
        self.SetSizer(wxScrollAreaSizer())

    def GetBestSize(self):
        """ An overridden parent class method which returns a sensible
        best size.

        The default wx implementation returns a best size of (16, 16)
        on Windows; far too small to be useful. So, we just adopt the
        size hint of (256, 192) used in Qt's QAbstractScrollArea.

        """
        return self._best_size

    def GetScrollWidget(self):
        """ Get the scroll widget for this scroll area.

        Returns
        -------
        results : wxWindow
            The wxWindow being scrolled by this scroll area.

        """
        return self._scroll_widget

    def SetScrollWidget(self, widget):
        """ Set the scroll widget for this scroll area.

        Parameters
        ----------
        widget : wxWindow
            The wxWindow which should be scrolled by this area.

        """
        self._scroll_widget = widget
        self.GetSizer().Add(widget)


class WxScrollArea(WxConstraintsWidget):
    """ A Wx implementation of an Enaml ScrollArea.

    """
    #: Storage for the scroll widget id
    _scroll_widget_id = None

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
        self.set_scroll_widget_id(tree['scroll_widget_id'])
        self.set_horizontal_scrollbar(tree['horizontal_scrollbar'])
        self.set_vertical_scrollbar(tree['vertical_scrollbar'])

    def init_layout(self):
        """ Handle the layout initialization for the scroll area.

        """
        child = self.find_child(self._scroll_widget_id)
        if child is not None:
            self.widget().SetScrollWidget(child.widget())

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_horizontal_scrollbar(self, content):
        """ Handle the 'set_horizontal_scrollbar' action from the Enaml
        widget.

        """
        self.set_horizontal_scrollbar(content['horizontal_scrollbar'])

    def on_action_set_vertical_scrollbar(self, content):
        """ Handle the 'set_vertical_scrollbar' action from the Enaml
        widget.

        """
        self.set_vertical_scrollbar(content['vertical_scrollbar'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_scroll_widget_id(self, widget_id):
        """ Set the scroll widget id for the underlying widget.

        """
        self._scroll_widget_id = widget_id

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

