#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_layout_component import WXLayoutComponent

from ..tab_group import AbstractTkTabGroup


#: A mapping from TabPosition enum values to qt tab positions.
_TAB_POSITION_MAP = {
    'top': wx.NB_TOP,
    'bottom': wx.NB_BOTTOM,
    'left': wx.NB_LEFT,
    'right': wx.NB_RIGHT,
}


class WXTabGroup(WXLayoutComponent, AbstractTkTabGroup):
    """ A wx implementation of the Tabbed container.

    """
    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying wxNotebook control.

        """
        # Changing the tab position of the notebook dynamically is not
        # supported by wx (the rendering gets all messed up). So, the
        # tab position must be set at creation time.
        style = _TAB_POSITION_MAP[self.shell_obj.tab_position]
        self.widget = wx.Notebook(parent, style=style)
    
    def initialize(self):
        """ Initialize the attributes of the wxNotebook.

        """
        super(WXTabGroup, self).initialize()
        self.update_tabs()
        self.set_selected_index(self.shell_obj.selected_index)

    def bind(self):
        """ Bind to the events emitted by the underlying control.

        """
        super(WXTabGroup, self).bind()
        self.widget.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_page_changed)

    #--------------------------------------------------------------------------
    # Implementation 
    #--------------------------------------------------------------------------
    def shell_tabs_changed(self, tabs):
        """ The change handler for the 'tabs' attribute of the shell 
        object.

        """
        self.update_tabs()

    def shell_tab_position_changed(self, tab_position):
        """ The change handler for the 'tab_position' attribute of the
        shell object.

        """
        # Changing tab position dynamically on wx is not supported.
        pass

    def shell_selected_index_changed(self, index):
        """ Update the widget index with the new value from the shell 
        object.

        """
        self.set_selected_index(index)

    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state. This
        value is used by the layout manager to determine how much
        space to allocate the widget.

        """
        # XXX - This size hint computation needs some work. Need to 
        # look at the source for wxNotebook::GetBestSize and see what
        # is does and compare against QTabWidget::sizeHint. Like always,
        # the Qt implementation does the right thing and wx does not.
        widget = self.widget
        shell = self.shell_obj
        curr_shell = shell.selected_tab

        if curr_shell is None:
            # QTabWidget default for no tabs
            return (6, 6)
        
        size_hint = curr_shell.size_hint()

        if size_hint == (-1, -1):
            size_hint = curr_shell.min_size()
        
        width_hint, height_hint = size_hint

        # Compute the size of the tab so we can offset the size hint.
        # On Windows, the return value of the height function is a hard
        # coded default of 20. This is close for the standard font but
        # will probably break down with different fonts or icons. I've
        # found no other way to measure the height of the tab bar.
        tab_size = wx.RendererNative.Get().GetHeaderButtonHeight(widget)

        # Offset the size hint by the tab bar size
        style = widget.GetWindowStyle()
        if (style & wx.NB_TOP) or (style & wx.NB_BOTTOM):
            height_hint += tab_size
        else:
            width_hint += tab_size
        
        width_hint = max(width_hint, 200)

        return (width_hint, height_hint)

    #--------------------------------------------------------------------------
    # Event Handlers 
    #--------------------------------------------------------------------------
    def _on_page_changed(self, event):
        """ The event handler for the page change event of the underlying 
        control. Synchronizes the index of the shell object.

        """
        event.Skip()
        # Use event.GetSelection since widget.GetSelection returns the
        # wrong value during this event handler.
        self.shell_obj._selected_index = event.GetSelection()

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_selected_index(self, index):
        """ Sets the current index of the tab widget. This is overridden
        from the parent class.

        """
        if index != -1:
            self.widget.SetSelection(index)
    
    def update_tabs(self):
        """ Populates the notebook with the child notebook pages. This
        is an overridden parent class method which sets the title of
        of notebook pages properly.

        """
        # FIXME: there should be a more efficient way to do this, but 
        # for now just remove all present widgets and add the current 
        # ones. If we use DeleteAllPages(), then the child widgets would
        # be destroyed, which is not the behavior we want.
        widget = self.widget
        shell = self.shell_obj
        while widget.GetPageCount():
            widget.RemovePage(0)
        for idx, tab in enumerate(shell.tabs):
            widget.AddPage(tab.toolkit_widget, tab.title)

        # This bit of logic is required or all the tabs draw on
        # top of themselves initially.
        selected = self.shell_obj.selected_tab
        if selected is not None:
            for idx, tab in enumerate(shell.tabs):
                if tab is not selected:
                    tab.set_visible(False)
                else:
                    tab.set_visible(True)
                    widget.SetSelection(idx)

