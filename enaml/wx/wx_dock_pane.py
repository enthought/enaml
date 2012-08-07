#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_widget_component import WxWidgetComponent


class wxDockPaneSizer(wx.PySizer):
    """ A custom wx.PySizer for use with a wxDockPane.

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
            res = super(wxDockPaneSizer, self).Add(widget)
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
        else:
            res = wx.Size(-1, -1)
        return res
    
    def RecalcSizes(self):
        """ Resizes the child to fit in the available space.

        """
        widget = self._widget
        if widget is not None:
            widget.SetSize(self.GetSize())


class wxDockPane(wx.Panel):
    """ A subclass of wx.PyPanel which acts as a dock pane.

    """
    def __init__(self, *args, **kwargs):
        super(wxDockPane, self).__init__(*args, **kwargs)
        self._title = u''

    def GetTitle(self):
        """ Return the title for the dock pane.

        Returns
        -------
        result : unicode
            The title of the dock pane.

        """
        return self._title

    def SetTitle(self, title):
        """ Set the title for the dock pane.

        Parameters
        ----------
        title : unicode
            The title to use for the dock pane.

        """
        self._title = title


class WxDockPane(WxWidgetComponent):
    """ A Wx implementation of an Enaml DockPane.

    """
    #: The storage for the dock widget id
    _dock_widget = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wxDockPane widget.

        """
        return wxDockPane(parent)

    def create(self, tree):
        """ Create and initialize the dock pane control.

        """
        super(WxDockPane, self).create(tree)
        self.set_dock_widget(tree['dock_widget'])

    def init_layout(self):
        """ Handle the layout initialization for the dock pane.

        """
        dock_widget = self._dock_widget
        for child in self.children:
            if child.widget_id == dock_widget:
                sizer = wxDockPaneSizer()
                sizer.Add(child.widget)
                self.widget.SetSizer(sizer)
                return

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------\
    def set_dock_widget(self, dock_widget):
        """ Set the dock widget for the underlying pane.

        """
        self._dock_widget = dock_widget

