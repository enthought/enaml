#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_single_widget_sizer import wxSingleWidgetSizer
from .wx_container import WxContainer
from .wx_widget import WxWidget


class wxSplitItem(wx.Panel):
    """ A wxPanel subclass which acts as an item in a wxSplitter.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxSplitItem.

        Parameters
        ----------
        *args, **kwargs
            The position and keyword arguments required to initialize
            a wxPanel.

        """
        super(wxSplitItem, self).__init__(*args, **kwargs)
        self._split_widget = None
        self.SetSizer(wxSingleWidgetSizer())

    def GetSplitWidget(self):
        """ Get the split widget for this split item.

        Returns
        -------
        result : wxWindow or None
            The split widget being managed by this item.

        """
        return self._split_widget

    def SetSplitWidget(self, widget):
        """ Set the split widget for this split item.

        Parameters
        ----------
        widget : wxWindow
            The wxWindow to use as the split widget in this item.

        """
        self._split_widget = widget
        self.GetSizer().Add(widget)


class WxSplitItem(WxWidget):
    """ A Wx implementation of an Enaml SplitItem.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QStackItem widget.

        """
        return wxSplitItem(parent)

    def create(self, tree):
        """ Create and initialize the underyling widget.

        """
        super(WxSplitItem, self).create(tree)
        self.set_preferred_size(tree['preferred_size'])

    def init_layout(self):
        """ Initialize the layout for the underyling widget.

        """
        super(WxSplitItem, self).init_layout()
        self.widget().SetSplitWidget(self.split_widget())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def split_widget(self):
        """ Find and return the split widget child for this widget.

        Returns
        -------
        result : wxWindow or None
            The split widget defined for this widget, or None if one is
            not defined.

        """
        widget = None
        for child in self.children():
            if isinstance(child, WxContainer):
                widget = child.widget()
        return widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a WxSplitItem.

        """
        if isinstance(child, WxContainer):
            self.widget().SetSplitWidget(self.split_widget())

    def child_added(self, child):
        """ Handle the child added event for a QtSplitItem.

        """
        if isinstance(child, WxContainer):
            self.widget().SetSplitWidget(self.split_widget())

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_preferred_size(self, content):
        """ Handle the 'set_preferred_size' action from the Enaml widget.

        """
        self.set_preferred_size(content['preferred_size'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_preferred_size(self, size):
        """ Set the preferred size for this item in the splitter.

        """
        # XXX implement me
        pass

