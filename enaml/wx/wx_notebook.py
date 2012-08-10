#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.aui
import wx.lib.newevent

from .wx_constraints_widget import WxConstraintsWidget


#: A mapping of notebook tab positions for the document style tabs.
_TAB_POSITION_MAP = {
    'top': wx.aui.AUI_NB_TOP,
    'left': wx.aui.AUI_NB_TOP,
    'bottom': wx.aui.AUI_NB_BOTTOM,
    'right': wx.aui.AUI_NB_BOTTOM,
}


#: A mask of notebook tab positions for the document style tabs.
_TAB_POSITION_MASK = wx.aui.AUI_NB_TOP | wx.aui.AUI_NB_BOTTOM


class wxNotebookMixin(object):
    """ A mixin class for the wxNotebook and wxAuiNotebook classes.

    This mixin provides the tab management functionality for opening
    and closing tabs while still maintaining the logical notebook
    ownership.
   
    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxNotebookMixin.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to pass to the super
            class.

        """
        super(wxNotebookMixin, self).__init__(*args, **kwargs)
        self._owned_pages = set()
        self._closed_pages = {}

    def HasPage(self, page):
        """ Whether or not the notebook owns the given page.

        Note that this method should be used instead of GetPageIndex.
        This method is faster, and will not give a False negative if 
        the page is closed instead of removed.

        Parameters
        ----------
        page : wxPage
            The wxPage instance to check for membership.

        Returns
        -------
        result : bool
            True if the notebook owns the page, False otherwise.

        """
        return page in self._owned_pages

    def OpenPage(self, page):
        """ Open a hidden page in the notebook.

        If the page does not belong to the notebook or is already open,
        then this method is a no-op.

        Parameters
        ----------
        page : wxPage
            The wxPage instance to open in the notebook.

        """
        if page not in self._owned_pages:
            return
        open_index = self._closed_pages.pop(page, None)
        if open_index is not None:
            title = page.GetTitle()
            super(wxNotebookMixin, self).InsertPage(open_index, page, title)

    def ClosePage(self, page):
        """ Close the given page in the notebook.

        If the page does not belong to the notebook or is already closed,
        then this method is a no-op.

        Parameters
        ----------
        page : wxPage
            The wxPage to close in the notebook.

        """
        if page not in self._owned_pages:
            return
        if page in self._closed_pages:
            return
        page_index = self.GetPageIndex(page)
        if page_index != -1:
            self._closed_pages[page] = page_index
            super(wxNotebookMixin, self).RemovePage(page_index)
            page.Show(False)
            
    def AddPage(self, page):
        """ Add a wxPage instance to the notebook.

        If the page already exists in the notebook, this is a no-op.

        Parameters
        ----------
        page : wxPage
            The wxPage instance to add to the notebook.

        """
        if page in self._owned_pages:
            return
        self._owned_pages.add(page)
        if page.IsOpen():
            super(wxNotebookMixin, self).AddPage(page, page.GetTitle())
        else:
            self._closed_pages[page] = self.GetPageCount()

    def InsertPage(self, index, page):
        """ Insert the page at the given index.

        If the page already exists in the notebook, this is a no-op.

        Parameters
        ----------
        index : int
            The integer index at which to insert the page.

        page : wxPage
            The wxPage instance to add to the notebook.

        """
        if page in self._owned_pages:
            return
        self._owned_pages.add(page)
        if page.IsOpen():
            title = page.GetTitle()
            super(wxNotebookMixin, self).InsertPage(index, page, title)
        else:
            self._closed_pages[page] = index

    def RemovePage(self, page):
        """ Remove the given page from the notebook.

        If the page is not owned by the notebook, this is a no-op.

        Parameters
        ----------
        page : wxPage
            The wxPage instance to add to the notebook.

        """
        if page not in self._owned_pages:
            return
        self._owned_pages.discard(page)
        self._closed_pages.pop(page, None)
        index = self.GetPageIndex(page)
        if index != -1:
            super(wxNotebookMixin, self).RemovePage(index)
            page.Show(False)


class wxNotebook(wxNotebookMixin, wx.Notebook):
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


class wxAuiNotebook(wxNotebookMixin, wx.aui.AuiNotebook):
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

        This handler passes the event to wxPage object and lets it
        handle the close event.

        """
        self.GetPage(event.GetSelection()).OnClose(event)

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
    #: Storage for the widget ids of the notebook pages.
    _page_ids = []

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
        return res

    def create(self, tree):
        """ Create and initialize the notebook control

        """
        super(WxNotebook, self).create(tree)
        self.set_page_ids(tree['page_ids'])
        self.set_tab_position(tree['tab_position'])
        self.set_tabs_closable(tree['tabs_closable'])
        self.set_tabs_movable(tree['tabs_movable'])

    def init_layout(self):
        """ Handle the layout initialization for the notebook.

        """
        super(WxNotebook, self).init_layout()
        widget = self.widget()
        find_child = self.find_child
        for page_id in self._page_ids:
            child = find_child(page_id)
            if child is not None:
                widget.AddPage(child.widget())

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

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_page_ids(self, page_ids):
        """ Set the page ids for the underlying widget.

        """
        self._page_ids = page_ids

    def set_tab_position(self, position):
        """ Set the position of the tab bar in the widget.

        """
        widget = self.widget()
        if isinstance(widget, wxNotebook):
            # The 'preferences' style wxNotebook only supports nice
            # looking tabs on the top, so changing the tab position 
            # is ignored for this style.
            return
        # The AuiNotebook only supports tabs on top or bottom. The tab
        # position map maps this discrepancy appropriately. We also 
        # need to trigger a full repaint, or we'll suffer rendering
        # artifacts when the tab position is dynamically changed.
        widget.WindowStyle &= ~_TAB_POSITION_MASK
        widget.WindowStyle |= _TAB_POSITION_MAP[position]
        widget.Refresh()

    def set_tab_style(self, style):
        """ Set the tab style for the tab bar in the widget.

        """
        # Dynamically changing the tab style is not supported on wx.
        pass

    def set_tabs_closable(self, closable):
        """ Set whether or not the tabs are closable.

        """
        widget = self.widget()
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
        widget = self.widget()
        if isinstance(widget, wxNotebook):
            # The 'preferences' style wxNotebook does not support
            # movable tabs, so that setting is simply ignored.
            return
        style = wx.aui.AUI_NB_TAB_MOVE | wx.aui.AUI_NB_TAB_SPLIT
        if movable:
            widget.WindowStyle |= style
        else:
            widget.WindowStyle &= ~style

