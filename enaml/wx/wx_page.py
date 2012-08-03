#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.lib.newevent

from .wx_container import WxContainer, wxContainer


#: An event emitted when a tab's title changes.
wxTabTitleEvent, EVT_TAB_TITLE = wx.lib.newevent.NewEvent()


#: An event emitted when a tab's tooltip changes.
wxTabToolTipEvent, EVT_TAB_TOOLTIP = wx.lib.newevent.NewEvent()


#: An event emitted when a tab's enabled state changes.
wxTabEnabledEvent, EVT_TAB_ENABLED = wx.lib.newevent.NewEvent()


#: An event emitted when a tab's closable state changes.
wxTabClosableEvent, EVT_TAB_CLOSABLE = wx.lib.newevent.NewEvent()


class wxPage(wxContainer):
    """ A wxContainer subclass which acts as a page in a wxNotebook.

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
        self._tab_tool_tip = u''
        self._tab_enabled = True
        self._tab_closable = True

    def GetTabTitle(self):
        """ Returns the tab title for this page.

        Returns
        -------
        result : unicode
            The title string for the page's tab.

        """
        return self._tab_title

    def SetTabTitle(self, title):
        """ Set the title for the tab for this page. This will emit the
        EVT_TAB_TITLE event.

        Parameters
        ----------
        title : unicode
            The string to use for this page's tab title.

        """
        self._tab_title = title
        event = wxTabTitleEvent(page=self, title=title)
        wx.PostEvent(self, event)

    def GetTabToolTip(self):
        """ Returns the tool tip for the tab for this page.

        Returns
        -------
        result : unicode
            The tool tip string for the page's tab.

        """
        return self._tab_tool_tip

    def SetTabToolTip(self, tool_tip):
        """ Set the tool tip for the tab for this page. This will emit
        the EVT_TAB_TOOLTIP event.

        Parameters
        ----------
        title : unicode
            The string to use for this page's tab tool tip.

        """
        self._tab_tool_tip = tool_tip
        event = wxTabToolTipEvent(page=self, tool_tip=tool_tip)
        wx.PostEvent(self, event)

    def GetTabEnabled(self):
        """ Return whether or no the tab for this page is enabled.

        Returns
        -------
        result : bool
            True if the tab for this page is enabled, False otherwise.

        """
        return self._tab_enabled

    def SetTabEnabled(self, enabled):
        """ Set whether the tab for this page is enabled. This will 
        emit the EVT_TAB_ENABLED event.

        Parameters
        ----------
        enabled : bool
            True if the tab should be enabled, False otherwise.

        """
        self._tab_enabled = enabled
        event = wxTabEnabledEvent(page=self, enabled=enabled)
        wx.PostEvent(self, event)

    def GetTabClosable(self):
        """ Returns whether or not the tab for this page is closable.

        Returns
        -------
        result : bool
            True if this page's tab is closable, False otherwise.

        """
        return self._tab_closable

    def SetTabClosable(self, closable):
        """ Set whether the tab for this page is closable. This will
        emit the EVT_TAB_CLOSABLE event.

        Parameters
        ----------
        closable : bool
            True if the tab should be closable, False otherwise.

        """
        self._tab_closable = closable
        event = wxTabClosableEvent(page=self, closable=closable)
        wx.PostEvent(self, event)


class WxPage(WxContainer):
    """ A Wx implementation of an Enaml notebook Page.

    """
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
        self.set_title(tree['title'])
        self.set_tool_tip(tree['tool_tip'])
        self.set_tab_enabled(tree['tab_enabled'])
        self.set_closable(tree['closable'])

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
    def set_title(self, title):
        """ Set the title of the tab for this page.

        """
        self.widget.SetTabTitle(title)

    def set_closable(self, closable):
        """ Set whether or not this page is closable.

        """
        self.widget.SetTabClosable(closable)

    def set_tool_tip(self, tool_tip):
        """ Set the tooltip of the tab for this page.

        """
        self.widget.SetTabToolTip(tool_tip)

    def set_tab_enabled(self, enabled):
        """ Set the enabled state for the tab for this page.

        """
        self.widget.SetTabEnabled(enabled)

    def set_visible(self, visible):
        """ Overriden method which disables the setting of visibility
        by the user code.

        The visibility of a page is controlled entirely by the parent
        WxNotebook.

        """
        pass

