#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_widget_component import WxWidgetComponent
from .wx_single_widget_sizer import wxSingleWidgetSizer


class wxTab(wx.Panel):
    """ A wxPanel subclass which acts as a tab in a wxTabControl.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxPage.

        Parameters
        ----------
        *args, **kwargs
            The position and keyword arguments required to initialize
            a wxContainer.

        """
        super(wxTab, self).__init__(*args, **kwargs)
        self._title = u''
        self._is_open = True
        self._tab_widget = None
        self.SetSizer(wxSingleWidgetSizer())

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _TabIndexOperation(self, closure):
        """ A private method which will run the given closure if there 
        is a valid index for this tab.

        """
        parent = self.GetParent()
        if parent:
            index = parent.GetTabIndex(self)
            if index != -1:
                closure(parent, index)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetTabWidget(self):
        """ Get the tab widget for this page.

        Returns
        -------
        result : wxWindow or None
            The tab widget being managed by this tab.

        """
        return self._tab_widget

    def SetTabWidget(self, widget):
        """ Set the tab widget for this tab.

        Parameters
        ----------
        widget : wxWindow
            The wx widget to use as the tab widget in this tab.

        """
        self._tab_widget = widget
        self.GetSizer().Add(widget)

    def IsOpen(self):
        """ Get whether or not the tab is open.

        Returns
        -------
        result : bool
            True if the tab is open, False otherwise.

        """
        return self._is_open

    def Open(self):
        """ Open the tab in the tab control.

        """
        self._is_open = True
        parent = self.GetParent()
        if parent:
            parent.ShowWxTab(self)

    def Close(self):
        """ Close the tab in the tab control.

        """
        self._is_open = False
        parent = self.GetParent()
        if parent:
            parent.HideWxTab(self) 

    def GetTitle(self):
        """ Returns tab title for this tab.

        Returns
        -------
        result : unicode
            The title string for the tab.

        """
        return self._title

    def SetTitle(self, title):
        """ Set the title for this tab.

        Parameters
        ----------
        title : unicode
            The string to use for this tab's title.

        """
        self._title = title
        def closure(nb, index):
            nb.SetPageText(index, title)
        self._TabIndexOperation(closure)


class WxTab(WxWidgetComponent):
    """ A Wx implementation of an Enaml Tab.

    """
    #: The storage for the tab widget id
    _tab_widget_id = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wxTab widget.

        """
        return wxTab(parent)

    def create(self, tree):
        """ Create and initialize the tab control.

        """
        super(WxTab, self).create(tree)
        self.set_tab_widget_id(tree['tab_widget_id'])
        self.set_title(tree['title'])
        self.set_tool_tip(tree['tool_tip'])

    def init_layout(self):
        """ Initialize the layout of the notebook page.

        """
        super(WxTab, self).init_layout()
        child = self.find_child(self._tab_widget_id)
        if child is not None:
            self.widget().SetTabWidget(child.widget())

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_title(self, content):
        """ Handle the 'set_title' action from the Enaml widget.

        """
        self.set_title(content['title'])

    def on_action_set_tool_tip(self, content):
        """ Handle the 'set_tool_tip' action from the Enaml widget.

        """
        self.set_tool_tip(content['tool_tip'])

    def on_action_open(self, content):
        """ Handle the 'open' action from the Enaml widget.

        """
        self.widget().Open()

    def on_action_close(self, content):
        """ Handle the 'close' action from the Enaml widget.

        """
        self.widget().Close()
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_visible(self, visible):
        """ An overridden visibility setter which to opens|closes the
        tab.

        """
        widget = self.widget()
        if visible:
            widget.Open()
        else:
            widget.Close()

    def set_tab_widget_id(self, widget_id):
        """ Set the tab widget id for the underlying control.

        """
        self._tab_widget_id = widget_id

    def set_title(self, title):
        """ Set the title of the tab.

        """
        self.widget().SetTitle(title)

    def set_tool_tip(self, tool_tip):
        """ Set the tooltip of the tab.

        """
        # XXX Wx notebooks do not support a tab tooltip, so this 
        # setting is simply ignored.
        pass

