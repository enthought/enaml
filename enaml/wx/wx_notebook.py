#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.aui
import wx.lib.newevent

from .wx_constraints_widget import WxConstraintsWidget
from .wx_page import EVT_TAB_TITLE


#: A mapping of notebook tab positions for the document style tabs.
_TAB_POSITION_MAP = {
    'top': wx.aui.AUI_NB_TOP,
    'left': wx.aui.AUI_NB_TOP,
    'bottom': wx.aui.AUI_NB_BOTTOM,
    'right': wx.aui.AUI_NB_BOTTOM,
}


#: A mask of notebook tab positions for the document style tabs.
_TAB_POSITION_MASK = wx.aui.AUI_NB_TOP | wx.aui.AUI_NB_BOTTOM


#: An event emitted when a page close is requested on the 'document' 
#: style notebook control.
wxPageCloseRequestEvent, EVT_PAGE_CLOSE_REQUEST = wx.lib.newevent.NewEvent()


class NotebookMixin(object):
    """ A mixin class which provides common functionality for both the 
    wxNotebook and wxAuiNotebook classes.

    """
    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _bind(self, page):
        """ Bind the signal handlers for the given page.

        """
        # The wx notebooks don't support tab tooltips, enabled state,
        # or individual close buttons, so we don't bind to those change 
        # events.
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
    def AddPage(self, page, idx=-1):
        """ Add a wxPage instance to the notebook.

        Parameters
        ----------
        page : wxPage
            The wxPage instance to add to the notebook.

        idx : int, optional
            The index at which to add the page if it doesn't already
            exist in the notebook. If not provided, the page will be
            added at the end of the notebook.

        """
        page_idx = self.GetPageIndex(page)
        if page_idx == -1:
            self._bind(page)
            if idx == -1:
                super(NotebookMixin, self).AddPage(page, page.GetTabTitle())
            else:
                self.InsertPage(idx, page, page.GetTabTitle())
        else:
            self.SetPageText(page_idx, page.GetTabTitle())

    def RemovePage(self, index):
        """ Remove the page at the given index.

        Parameters
        ----------
        index : int
            The index of the page to remove from the notebook.

        """
        # This check prevents exceptions and segfaults in case we 
        # get a -1 or a value out of range.
        if index < 0 or index >= self.GetPageCount():
            return
        page = self.GetPage(index)
        if page is not None:
            self._unbind(page)
            super(NotebookMixin, self).RemovePage(index)
            page.Show(False)


class wxNotebook(NotebookMixin, wx.Notebook):
    """ A custom wx.Notebook which handles children of type wxPage.

    This notebook control is used for the 'preferences' tab style.

    """
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


class wxAuiNotebook(NotebookMixin, wx.aui.AuiNotebook):
    """ A custom wx AuiNotebook which handles children of type wxPage.

    This notebook control is used for the 'document' tab style.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxAuiNotebook.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to initialize a
            wx.aui.AuiNotebook.

        """
        super(wxAuiNotebook, self).__init__(*args, **kwargs)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self._OnPageClose)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _OnPageClose(self, event):
        """ The handler for the EVT_AUINOTEBOOK_PAGE_CLOSE event.

        This handler vetos each event and emits its own event if the 
        page is marked as closable. It is important to veto the event
        since the default wx behavior when closing a page is to destroy
        it, rather than remove it.

        """
        event.Veto()
        index = event.GetSelection()
        page = self.GetPage(index)
        if page.GetTabClosable():
            event = wxPageCloseRequestEvent(index=index)
            wx.PostEvent(self, event)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetBestSize(self):
        """ Overridden GetBestSize method which will return the best
        size for the current tab.

        """
        page = self.GetCurrentPage()
        if page is None:
            return super(wxAuiNotebook, self).GetBestSize()
        # On windows, the wx.AuiNotebook the page with a bit of padding
        # on all sides. The height can be determined automatically by 
        # the notebook, but it's off by about 4 pixels (go figure...). 
        # The width padding was measured manually.
        size = page.GetBestSize()
        height = self.GetHeightForPageHeight(size.GetHeight())
        return wx.Size(size.GetWidth() + 6, height + 4)

    def GetCurrentPage(self):
        """ Returns the currently selected page, or None if there is
        no selected page.

        """
        # So the wx.Notebook provides no native way to get the index of
        # a particular page, and this notebook provides no native way to
        # get the currently selected page. Again, hooray for brain-dead
        # toolkits...
        idx = self.GetSelection()
        if idx == -1:
            return None
        return self.GetPage(idx)


class WxNotebook(WxConstraintsWidget):
    """ A Wx implementation of an Enaml Notebook.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wx notebook widget.

        """
        # We have to choose the notebook style at startup since we have
        # to use a completely different control. Thus, switching between
        # document and preference style tabs is not supported.
        if tree['tab_style'] == 'preferences':
            res = wxNotebook(parent)
        else:
            res = wxAuiNotebook(parent, style=wx.aui.AUI_NB_SCROLL_BUTTONS)
            res.Bind(EVT_PAGE_CLOSE_REQUEST, self.on_page_close_requested)
        return res

    def create(self, tree):
        """ Create and initialize the notebook control

        """
        super(WxNotebook, self).create(tree)
        self.set_tab_position(tree['tab_position'])
        self.set_tabs_closable(tree['tabs_closable'])
        self.set_tabs_movable(tree['tabs_movable'])

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
                # Try to re-open the page in the original position. This
                # makes most sense for a 'preferences' style notebook, 
                # since it doesn't support movable tabs. We can hope for
                # "good enough" on the 'document' style tabs where the
                # child may have been moved around.
                self.widget.AddPage(child.widget, idx)

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
    def on_page_close_requested(self, event):
        """ The signal handler for the 'EVT_PAGE_CLOSE_REQUEST' event.

        This handler is only bound for 'document' style notebook tabs, 
        and it is only called when the page is marked as closable.

        """
        index = event.index
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
        # The AuiNotebook only supports tabs on top or bottom. The tab
        # position map maps this discrepancy appropriately.
        widget.WindowStyle &= ~_TAB_POSITION_MASK
        widget.WindowStyle |= _TAB_POSITION_MAP[position]
        # Need to trigger a full repaint, or we'll suffer rendering
        # artifacts when the tab position is dynamically changed.
        widget.Refresh()

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
            # with close buttons, so that setting is simply ignored.
            return
        if closable:
            widget.WindowStyle |= wx.aui.AUI_NB_CLOSE_ON_ALL_TABS
        else:
            widget.WindowStyle &= ~wx.aui.AUI_NB_CLOSE_ON_ALL_TABS

    def set_tabs_movable(self, movable):
        """ Set whether or not the tabs are movable.

        """
        widget = self.widget
        if isinstance(widget, wxNotebook):
            # The 'preferences' style wxNotebook does not support
            # movable tabs, so that setting is simply ignored.
            return
        style = wx.aui.AUI_NB_TAB_MOVE | wx.aui.AUI_NB_TAB_SPLIT
        if movable:
            widget.WindowStyle |= style
        else:
            widget.WindowStyle &= ~style

