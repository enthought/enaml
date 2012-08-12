#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref
import wx

from .wx_constraints_widget import WxConstraintsWidget
from .wx_upstream import aui


#: A mapping of notebook tab positions for the document style tabs.
#: Wx currently only supports top and bottom tab positions.
_TAB_POSITION_MAP = {
    'top': aui.AUI_NB_TOP,
    'left': aui.AUI_NB_TOP,
    'bottom': aui.AUI_NB_BOTTOM,
    'right': aui.AUI_NB_BOTTOM,
}


#: A mask of notebook tab positions for the document style tabs.
_TAB_POSITION_MASK = aui.AUI_NB_TOP | aui.AUI_NB_BOTTOM


class wxAuiNotebook(aui.AuiNotebook):
    """ A custom wx AuiNotebook which handles children of type wxPage.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxNotebookMixin.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to pass to the super
            class.

        """
        super(wxAuiNotebook, self).__init__(*args, **kwargs)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClose)
        self._hidden_pages = weakref.WeakKeyDictionary()

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def OnPageClose(self, event):
        """ The handler for the EVT_AUINOTEBOOK_PAGE_CLOSE event.

        This handler forwards the event to the wxPage instance.

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
            return wx.Size(256, 192)
        # On windows, there's an off by 2 error in the width.
        size = page.GetBestSize()
        height = self.GetHeightForPageHeight(size.GetHeight())
        return wx.Size(size.GetWidth() + 2, height)

    def ShowWxPage(self, page):
        """ Show a hidden wxPage instance in the notebook.

        If the page is not owned by the notebook, this is a no-op.

        Parameters
        ----------
        page : wxPage
            The hidden wxPage instance to show in the notebook.

        """
        index = self.GetPageIndex(page)
        if index == -1:
            index = self._hidden_pages.pop(page, -1)
            if index != -1:
                self.InsertWxPage(index, page)

    def HideWxPage(self, page):
        """ Hide the given wxPage instance in the notebook.

        If the page is not owned by the notebook, this is a no-op.

        Parameters
        ----------
        page : wxPage
            The wxPage instance to hide in the notebook.

        """
        index = self.GetPageIndex(page)
        if index != -1:
            self.RemovePage(index)
            page.Show(False)
            self._hidden_pages[page] = index

    def AddWxPage(self, page):
        """ Add a wxPage instance to the notebook.

        This should be used in favor of AddPage for adding a wxPage
        instance to the notebook, as it takes into account the current
        page state.

        Parameters
        ----------
        page : wxPage
            The wxPage instance to add to the notebook.

        """
        if page.IsOpen():
            self.AddPage(page, page.GetTitle())
            index = self.GetPageIndex(page)
            if not page.GetEnabled():
                self.EnableTab(index, False)
            if not page.GetClosable():
                self.SetCloseButton(index, False)
        else:
            page.Show(False)
            self._hidden_pages[page] = self.GetPageCount()

    def InsertWxPage(self, index, page):
        """ Insert a wxPage instance into the notebook.

        This should be used in favor of InsertPage for inserting a
        wxPage instance into the notebook, as it takes into account the
        current page state.

        Parameters
        ----------
        index : int
            The index at which to insert the page.

        page : wxPage
            The wxPage instance to add to the notebook.

        """
        if page.IsOpen():
            self.InsertPage(index, page, page.GetTitle())
            if not page.GetEnabled():
                self.EnableTab(index, False)
            if not page.GetClosable():
                self.SetCloseButton(index, False)
        else:
            page.Show(False)
            self._hidden_pages[page] = index


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
        return wxAuiNotebook(parent, agwStyle=aui.AUI_NB_SCROLL_BUTTONS)

    def create(self, tree):
        """ Create and initialize the notebook control

        """
        super(WxNotebook, self).create(tree)
        self.set_page_ids(tree['page_ids'])
        self.set_tab_position(tree['tab_position'])
        self.set_tabs_closable(tree['tabs_closable'])
        self.set_tabs_movable(tree['tabs_movable'])
        self.set_tabs_dockable(tree['tabs_dockable'])

    def init_layout(self):
        """ Handle the layout initialization for the notebook.

        """
        super(WxNotebook, self).init_layout()
        widget = self.widget()
        find_child = self.find_child
        for page_id in self._page_ids:
            child = find_child(page_id)
            if child is not None:
                widget.AddWxPage(child.widget())

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_tab_position(self, content):
        """ Handle the 'set_tab_position' action from the Enaml widget.

        """
        self.set_tab_position(content['tab_position'])

    def on_action_set_tabs_closable(self, content):
        """ Handle the 'set_tabs_closable' action from the Enaml widget.

        """
        self.set_tabs_closable(content['tabs_closable'])

    def on_action_set_tabs_movable(self, content):
        """ Handle the 'set_tabs_movable' action from the Enaml widget.

        """
        self.set_tabs_movable(content['tabs_movable'])

    def on_action_set_tabs_dockable(self, content):
        """ Handle the 'set_tabs_dockable' action from the Enaml widget.

        """
        self.set_tabs_dockable(content['tabs_dockable'])

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
        flags = widget.GetAGWWindowStyleFlag()
        flags &= ~_TAB_POSITION_MASK
        flags |= _TAB_POSITION_MAP[position]
        widget.SetAGWWindowStyleFlag(flags)
        widget.Refresh() # Avoids rendering artifacts

    def set_tabs_closable(self, closable):
        """ Set whether or not the tabs are closable.

        """
        widget = self.widget()
        flags = widget.GetAGWWindowStyleFlag()
        if closable:
            flags |= aui.AUI_NB_CLOSE_ON_ALL_TABS
        else:
            flags &= ~aui.AUI_NB_CLOSE_ON_ALL_TABS
        widget.SetAGWWindowStyleFlag(flags)

    def set_tabs_movable(self, movable):
        """ Set whether or not the tabs are movable.

        """
        widget = self.widget()
        flags = widget.GetAGWWindowStyleFlag()
        if movable:
           flags |= aui.AUI_NB_TAB_MOVE
        else:
           flags &= ~aui.AUI_NB_TAB_MOVE
        widget.SetAGWWindowStyleFlag(flags)

    def set_tabs_dockable(self, dockable):
        """ Set whether or not the tabs are dockable.

        """
        widget = self.widget()
        flags = widget.GetAGWWindowStyleFlag()
        if dockable:
           flags |= aui.AUI_NB_TAB_SPLIT
        else:
           flags &= ~aui.AUI_NB_TAB_SPLIT
        widget.SetAGWWindowStyleFlag(flags)

