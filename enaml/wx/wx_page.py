#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.lib.newevent

from .wx_widget_component import WxWidgetComponent
from .wx_single_widget_sizer import wxSingleWidgetSizer


#: An event emitted when the notebook page is closed.
wxPageClosedEvent, EVT_PAGE_CLOSED = wx.lib.newevent.NewEvent()


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
        self._title = u''
        self._closable = True
        self._page_widget = None
        self._is_open = True
        self.SetSizer(wxSingleWidgetSizer())

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def OnClose(self, event):
        """ Handle the page close event.

        This event handler is called by the parent notebook. The parent
        event is always be vetoed or else Wx will destroy the page. If 
        the page is closable, we close the page and emit the custom
        close event.

        """
        event.Veto()
        if self.GetClosable():
            self._is_open = False
            parent = self.GetParent()
            if parent:
                parent.ClosePage(self)
            self.Show(False)
            evt = wxPageClosedEvent()
            wx.PostEvent(self, evt)

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

    def IsOpen(self):
        """ Get whether or not the page is open.

        Returns
        -------
        result : bool
            True if the page is be open, False otherwise.

        """
        return self._is_open

    def Open(self):
        """ Open the page in the notebook.

        If the page is already open, this method is a no-op.

        """
        self._is_open = True
        parent = self.GetParent()
        if parent:
            parent.OpenPage(self)
        # We don't Show(True) here since visibility is at this point
        # the responsibility of the notebook.

    def Close(self):
        """ Close the dock pane in the main window.

        If the pane is already closed, this method is no-op.

        """
        self._is_open = False
        parent = self.GetParent()
        if parent:
            parent.ClosePage(self)
        self.Show(False)

    def GetTitle(self):
        """ Returns tab title for this page.

        Returns
        -------
        result : unicode
            The title string for the page's tab.

        """
        return self._title

    def SetTitle(self, title):
        """ Set the title for this page.

        Parameters
        ----------
        title : unicode
            The string to use for this page's tab title.

        """
        self._title = title
        parent = self.GetParent()
        if parent:
            index = parent.GetPageIndex(self)
            if index != -1:
                parent.SetPageText(index, title)

    def GetClosable(self):
        """ Returns whether or not this page is closable.

        Returns
        -------
        result : bool
            True if this page is closable, False otherwise.

        """
        return self._closable

    def SetClosable(self, closable):
        """ Set whether this page is closable.

        Parameters
        ----------
        closable : bool
            True if this page should be closable, False otherwise.

        """
        self._closable = closable


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
        self.set_closable(tree['closable'])
        self.widget().Bind(EVT_PAGE_CLOSED, self.on_page_closed)

    def init_layout(self):
        """ Initialize the layout of the notebook page.

        """
        super(WxPage, self).init_layout()
        child = self.find_child(self._page_widget_id)
        if child is not None:
            self.widget().SetPageWidget(child.widget())

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_page_closed(self, event):
        """ The event handler for the EVT_PAGE_CLOSED event.

        """
        self.send_action('closed', {})

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

    def on_action_set_closable(self, content):
        """ Handle the 'set_closable' action from the Enaml widget.

        """
        self.set_closable(content['closable'])

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
        notebook page.

        """
        widget = self.widget()
        if visible:
            widget.Open()
        else:
            widget.Close()

    def set_page_widget_id(self, widget_id):
        """ Set the page widget id for the underlying control.

        """
        self._page_widget_id = widget_id

    def set_title(self, title):
        """ Set the title of the tab for this page.

        """
        self.widget().SetTitle(title)

    def set_closable(self, closable):
        """ Set whether or not this page is closable.

        """
        self.widget().SetClosable(closable)

    def set_tool_tip(self, tool_tip):
        """ Set the tooltip of the tab for this page.

        """
        # XXX Wx notebooks do not support a tab tooltip, so this 
        # setting is simply ignored.
        pass

