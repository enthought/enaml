#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.lib.newevent

from .wx_constraints_widget import WxConstraintsWidget
from .wx_page import EVT_TAB_TITLE


#: An event emitted when a page close is requested on the 'document' 
#: style notebook control.
wxPageCloseRequestEvent, EVT_PAGE_CLOSE_REQUEST = wx.lib.newevent.NewEvent()


class wxNotebook(wx.Notebook):
    """ A custom wx.Notebook which handles children of type wxPage.

    This notebook control is used for 'preferences' tab style.

    """
    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _bind(self, page):
        """ Bind the signal handlers for the given page.

        """
        # The wx.Notebook doesn't support tab tooltips, enabled state,
        # or close buttons, so we don't bind to those change events.
        page.Bind(EVT_TAB_TITLE, self._OnTabTitleChanged)

    def _unbind(self, page):
        """ Unbind the signal handlers for the given page.

        """
        page.Unbind(EVT_TAB_TITLE, handler=self._OnTabTitleChanged)

    def _OnTabTitleChanged(self, event):
        """ The handler for the 'EVT_TAB_TITLE' event on a child page.

        """
        idx = self.GetPageIndex(event.page)
        if idx != -1:
            self.SetPageText(idx, event.title)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetBestSize(self):
        """ Overridden GetBestSize method which will return the best
        size for the current tab.

        """
        page = self.GetCurrentPage()
        if page is None:
            return super(wxNotebook, self).GetBestSize()
        # On windows, the wx.Notebook renders each page with 2 pixels
        # of padding on the top, right and bottom, and 4 pixels of 
        # padding on the left (at least under the Windows 7 theme).
        # We need to compensate for this padding along with the space
        # taken up by the tab bar. The tab bar height was manually 
        # measured to be 21 pixels. I've found no way to have wx measure
        # it for me (there's nothing in RendererNative for it), so its 
        # just hard-coded for now.
        size = page.GetBestSize()
        return wx.Size(size.GetWidth() + 6, size.GetHeight() + 25)

    def GetPageIndex(self, page):
        """ Returns the index of the page in the notebook.

        Parameters
        ----------
        page : wxPage
            The wxPage instance in the notebook.

        Returns
        -------
        result : int
            The index of the page in the notebook, or -1 if the page is
            not found.

        """
        # Wx has no way of querying for the index of a page, so we must
        # linear search ourselves. Hooray for brain-dead toolkits!
        for idx in range(self.GetPageCount()):
            if self.GetPage(idx) == page:
                return idx
        return -1

    def AddPage(self, page, idx=-1):
        """ Add a wxPage instance to the notebook.

        Parameters
        ----------
        page : wxPage
            The wxPage instance to add to the notebook.

        idx : int, optional
            The index at which to add the page if it doesn't already
            exist in the notebook. If not provided, the page will be
            added at the end.

        """
        page_idx = self.GetPageIndex(page)
        if page_idx == -1:
            self._bind(page)
            if idx == -1:
                super(wxNotebook, self).AddPage(page, page.GetTabTitle())
            else:
                self.InsertPage(idx, page, page.GetTabTitle())
        else:
            self.SetPageText(page_idx, page.GetTabTitle())

    def RemovePage(self, index):
        """ Remove the page at the given index. This method should be
        used in favor of the 'removeTab' method of the parent class.

        Parameters
        ----------
        index : int
            The index of the page to remove from the notebook.

        """
        page = self.GetPage(index)
        if page is not None:
            self._unbind(page)
            super(wxNotebook, self).RemovePage(index)


class WxNotebook(WxConstraintsWidget):
    """ A Wx implementation of an Enaml Notebook.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wx notebook widget.

        """
        # We have to choose the notebook style and tab position at 
        # startup, since we have to use a different control. Switching
        # between document and preference style tabs dynamically is 
        # therefore not supported.
        if tree['tab_style'] == 'preferences':
            return wxNotebook(parent)
        # XXX haven't yet added the aui book
        return wxNotebook(parent)

    def create(self, tree):
        """ Create and initialize the notebook control

        """
        super(WxNotebook, self).create(tree)
        self.set_tab_position(tree['tab_position'])
        self.set_tabs_closable(tree['tabs_closable'])
        self.set_tabs_movable(tree['tabs_movable'])
        #self.widget.pageCloseRequested.connect(self.on_page_close_requested)

    def post_create(self):
        """ Handle the post creation work for the notebook.

        This method explicitly adds the child wxPage instances to the
        underlying wxNotebook control.

        """
        super(WxNotebook, self).post_create()
        widget = self.widget
        for child in self.children:
            widget.AddPage(child.widget)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_tab_position(self, content):
        """ Handle the 'set_tab_position' action from the Enaml widget.

        """
        self.set_tab_position(content['tab_position'])
        
    def on_action_set_tab_style(self, content):
        """ Handle the 'set_tab_style' action from the Enaml widget.

        """
        self.set_tab_style(content['tab_style'])

    def on_action_set_tabs_closable(self, content):
        """ Handle the 'set_tabs_closable' action from the Enaml widget.

        """
        self.set_tabs_closable(content['tabs_closable'])

    def on_action_set_tabs_movable(self, content):
        """ Handle the 'set_tabs_movable' action from the Enaml widget.

        """
        self.set_tabs_movable(content['tabs_movable'])

    def on_action_open_tab(self, content):
        """ Handle the 'open_tab' action from the Enaml widget.

        """
        widget_id = content['widget_id']
        for idx, child in enumerate(self.children):
            if child.widget_id == widget_id:
                widget = self.widget
                if isinstance(widget, wxNotebook):
                    # Re-open the page in the original position when
                    # using the 'preferences' style notebook. Since 
                    # it doesn't support movable tabs the position of
                    # a child is deterministic.
                    self.widget.AddPage(child.widget, idx)
                    return

    def on_action_close_tab(self, content):
        """ Handle the 'close_tab' action from the Enaml widget.

        """
        widget_id = content['widget_id']
        for child in self.children:
            if child.widget_id == widget_id:
                widget = self.widget
                widget.RemovePage(widget.GetPageIndex(child.widget))
                return

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_page_close_requested(self, index):
        """ The signal handler for the 'EVT_PAGE_CLOSE_REQUEST' event.

        """
        page = self.widget.GetPage(index)
        self.widget.RemovePage(index)
        for child in self.children:
            if page == child.widget:
                widget_id = child.widget_id
                content = {'widget_id': widget_id}
                self.send_action('tab_closed', content)
                return

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_tab_position(self, position):
        """ Set the position of the tab bar in the widget.

        """
        widget = self.widget
        if isinstance(widget, wxNotebook):
            # The 'preferences' style wxNotebook only supports nice
            # looking tabs on the top, so changing the tab position 
            # is ignored for this style.
            return

    def set_tab_style(self, style):
        """ Set the tab style for the tab bar in the widget.

        """
        # Dynamically changing the tab style is not supported on wx.
        pass

    def set_tabs_closable(self, closable):
        """ Set whether or not the tabs are closable.

        """
        widget = self.widget
        if isinstance(widget, wxNotebook):
            # The 'preferences' style wxNotebook does not support tabs 
            # with close buttons, so that setting is ignored.
            return

    def set_tabs_movable(self, movable):
        """ Set whether or not the tabs are movable.

        """
        widget = self.widget
        if isinstance(widget, wxNotebook):
            # The 'preferences' style wxNotebook does not support
            # movable tabs, so that setting is ignored.
            return

