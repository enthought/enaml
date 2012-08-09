#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_widget_component import WxWidgetComponent
from .wx_single_widget_sizer import wxSingleWidgetSizer


class wxPage(wx.Panel):
    """ A wxPanel subclass which acts as a page in a wxNotebook.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxPage.

        Parameters
        ----------
        *args, **kwargs
            The position and keyword arguments required to initialize
            a wxContainer.

        """
        super(wxPage, self).__init__(*args, **kwargs)
        self._tab_title = u''
        self._widget_enabled = True
        self._tab_enabled = True
        self._tab_closable = True
        self._page_widget = None
        self.SetSizer(wxSingleWidgetSizer())

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def Enable(self, enabled):
        """ An overridden parent class method for setting the enabled
        state of a tab.

        Wx notebooks do not support enabled state for a tab, so we just
        overload it with the enabled state of the widget.

        """
        self._widget_enabled = enabled
        if (enabled and self._tab_enabled) or not enabled:
            super(wxPage, self).Enable(enabled)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetPageWidget(self):
        """ Get the page widget for this page.

        Returns
        -------
        result : wxWindow or None
            The page widget being managed by this page.

        """
        return self._page_widget

    def SetPageWidget(self, widget):
        """ Set the page widget for this page.

        Parameters
        ----------
        widget : wxWindow
            The wx widget to use as the page widget in this page.

        """
        self._page_widget = widget
        self.GetSizer().Add(widget)

    def GetTabTitle(self):
        """ Returns the tab title for this page.

        Returns
        -------
        result : unicode
            The title string for the page's tab.

        """
        return self._tab_title

    def SetTabTitle(self, title):
        """ Set the title for the tab for this page.

        Parameters
        ----------
        title : unicode
            The string to use for this page's tab title.

        """
        self._tab_title = title
        parent = self.GetParent()
        if parent:
            index = parent.GetPageIndex(self)
            if index != -1:
                parent.SetPageText(index, title)

    def GetTabEnabled(self):
        """ Return whether or no the tab for this page is enabled.

        Returns
        -------
        result : bool
            True if the tab for this page is enabled, False otherwise.

        """
        return self._tab_enabled

    def SetTabEnabled(self, enabled):
        """ Set whether the tab for this page is enabled.

        Parameters
        ----------
        enabled : bool
            True if the tab should be enabled, False otherwise.

        """
        self._tab_enabled = enabled
        if (enabled and self._widget_enabled) or not enabled:
            super(wxPage, self).Enable(enabled)

    def GetTabClosable(self):
        """ Returns whether or not the tab for this page is closable.

        Returns
        -------
        result : bool
            True if this page's tab is closable, False otherwise.

        """
        return self._tab_closable

    def SetTabClosable(self, closable):
        """ Set whether the tab for this page is closable.

        Parameters
        ----------
        closable : bool
            True if the tab should be closable, False otherwise.

        """
        self._tab_closable = closable


class WxPage(WxWidgetComponent):
    """ A Wx implementation of an Enaml notebook Page.

    """
    #: The storage for the page widget id
    _page_widget_id = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wxPage widget.

        """
        return wxPage(parent)

    def create(self, tree):
        """ Create and initialize the page control.

        """
        super(WxPage, self).create(tree)
        self.set_page_widget_id(tree['page_widget_id'])
        self.set_title(tree['title'])
        self.set_tool_tip(tree['tool_tip'])
        self.set_tab_enabled(tree['tab_enabled'])
        self.set_closable(tree['closable'])

    def init_layout(self):
        """ Initialize the layout of the notebook page.

        """
        super(WxPage, self).init_layout()
        child = self.find_child(self._page_widget_id)
        if child is not None:
            self.widget().SetPageWidget(child.widget())

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

    def on_action_set_tab_enabled(self, content):
        """ Handle the 'set_tab_enabled' action from the Enaml widget.

        """
        self.set_tab_enabled(content['tab_enabled'])

    def on_action_set_closable(self, content):
        """ Handle the 'set_closable' action from the Enaml widget.

        """
        self.set_closable(content['closable'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_page_widget_id(self, widget_id):
        """ Set the page widget id for the underlying control.

        """
        self._page_widget_id = widget_id

    def set_title(self, title):
        """ Set the title of the tab for this page.

        """
        self.widget().SetTabTitle(title)

    def set_closable(self, closable):
        """ Set whether or not this page is closable.

        """
        self.widget().SetTabClosable(closable)

    def set_tool_tip(self, tool_tip):
        """ Set the tooltip of the tab for this page.

        """
        # XXX Wx notebooks do not support a tab tooltip, so this 
        # setting is simply ignored.
        pass

    def set_tab_enabled(self, enabled):
        """ Set the enabled state for the tab for this page.

        """
        self.widget().SetTabEnabled(enabled)

    def set_visible(self, visible):
        """ Overriden method which disables the setting of visibility
        by the user code.

        The visibility of a page is controlled entirely by the parent
        WxNotebook.

        """
        pass

