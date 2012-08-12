#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref
import wx

from .wx_constraints_widget import WxConstraintsWidget


class wxTabControl(wx.Notebook):
    """ A custom wx.Notebook which handles children of type wxTab.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxTabControl.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to pass to the super
            class.

        """
        super(wxTabControl, self).__init__(*args, **kwargs)
        self._hidden_tabs = weakref.WeakKeyDictionary()

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
        # On windows, the wx.Notebook renders each page with 2 pixels
        # of padding on the top, and bottom, and 4 pixels of padding
        # on the left and right (at least under the Windows 7 theme).
        # We need to compensate for this padding along with the space
        # taken up by the tab bar. The tab bar height was manually 
        # measured to be 21 pixels. I've found no way to have wx measure
        # it for me (there's nothing in RendererNative for it), so its 
        # just hard-coded for now.
        size = page.GetBestSize()
        return wx.Size(size.GetWidth() + 8, size.GetHeight() + 25)

    def ShowWxTab(self, tab):
        """ Show a hidden wxTab instance in the control.

        If the tab is not owned by the control, this is a no-op.

        Parameters
        ----------
        tab : wxTab
            The hidden wxTab instance to show in the control.

        """
        index = self.GetTabIndex(tab)
        if index == -1:
            index = self._hidden_tabs.pop(tab, -1)
            if index != -1:
                self.InsertWxTab(index, tab)

    def HideWxTab(self, tab):
        """ Hide the given wxTab instance in the control.

        If the tab is not owned by the control, this is a no-op.

        Parameters
        ----------
        tab : wxTab
            The wxTab instance to hide in the control.

        """
        index = self.GetTabIndex(tab)
        if index != -1:
            self.RemovePage(index)
            tab.Show(False)
            self._hidden_tabs[tab] = index

    def AddWxTab(self, tab):
        """ Add a wxTab instance to the control.

        This should be used in favor of AddPage for adding a wxTab
        instance to the control, as it takes into account the current
        tab state.

        Parameters
        ----------
        tab : wxTab
            The wxTab instance to add to the control.

        """
        if tab.IsOpen():
            self.AddPage(tab, tab.GetTitle())
        else:
            tab.Show(False)
            self._hidden_tabs[tab] = self.GetPageCount()

    def InsertWxTab(self, index, tab):
        """ Insert a wxTab instance into the control.

        This should be used in favor of InsertPage for inserting a
        wxTab instance into the control, as it takes into account the
        current tab state.

        Parameters
        ----------
        index : int
            The index at which to insert the tab.

        tab : wxTab
            The wxTab instance to add to the control.

        """
        if tab.IsOpen():
            count = self.GetPageCount()
            if index >= count:
                index = count
            self.InsertPage(index, tab, tab.GetTitle())
        else:
            tab.Show(False)
            self._hidden_tabs[tab] = index

    def GetTabIndex(self, tab):
        """ Returns the index of the tab in the control.

        Parameters
        ----------
        tab : wxTab
            The wxTab instance in the control.

        Returns
        -------
        result : int
            The index of the tab in the control, or -1 if the tab is
            not found.

        """
        # Wx has no way of querying for the index of a page, so we must
        # linear search ourselves. Hooray for brain-dead toolkits!
        for idx in xrange(self.GetPageCount()):
            if self.GetPage(idx) == tab:
                return idx
        return -1


class WxTabControl(WxConstraintsWidget):
    """ A Wx implementation of an Enaml TabControl.

    """
    #: Storage for the widget ids of the control's tabs.
    _tab_ids = []

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wx tab control.

        """
        return wxTabControl(parent)

    def create(self, tree):
        """ Create and initialize the tab control

        """
        super(WxTabControl, self).create(tree)
        self.set_tab_ids(tree['tab_ids'])
        self.set_tab_position(tree['tab_position'])

    def init_layout(self):
        """ Handle the layout initialization for the tab.

        """
        super(WxTabControl, self).init_layout()
        widget = self.widget()
        find_child = self.find_child
        for tab_id in self._tab_ids:
            child = find_child(tab_id)
            if child is not None:
                widget.AddWxTab(child.widget())

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_tab_position(self, content):
        """ Handle the 'set_tab_position' action from the Enaml widget.

        """
        self.set_tab_position(content['tab_position'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_tab_ids(self, tab_ids):
        """ Set the tab ids for the underlying widget.

        """
        self._tab_ids = tab_ids

    def set_tab_position(self, position):
        """ Set the position of the tab bar in the widget.

        """
        # The wx.Notebook only supports nice looking tops in the 
        # default top position on Windows, so we don't support 
        # changing it.
        pass

