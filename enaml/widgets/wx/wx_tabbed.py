#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_stacked import WXStacked

from ..tabbed import AbstractTkTabbed


#: A mapping from TabPosition enum values to qt tab positions.
_TAB_POSITION_MAP = {
    'top': wx.NB_TOP,
    'bottom': wx.NB_BOTTOM,
    'left': wx.NB_LEFT,
    'right': wx.NB_RIGHT,
}


class WXTabbed(WXStacked, AbstractTkTabbed):
    """ A wx implementation of the Tabbed container.

    """
    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def create(self):
        """ Create the underlying QTabWidget control.

        """
        # Changing the tab position of the notebook dynamically is not
        # supported by wx (the rendering gets all messed up). So, the
        # tab position must be set at creation time.
        style = _TAB_POSITION_MAP[self.shell_obj.tab_position]
        self.widget = wx.Notebook(self.parent_widget(), style=style)
    
    def bind(self):
        """ Bind to the events emitted by the underlying control.

        """
        super(WXTabbed, self).bind()
        self.widget.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_page_changed)

    #--------------------------------------------------------------------------
    # Implementation 
    #--------------------------------------------------------------------------
    def shell_tab_position_changed(self, tab_position):
        """ The change handler for the 'tab_position' attribute of the
        shell object.

        """
        # Changing tab position dynamically on wx is not supported.
        pass

    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state. This
        value is used by the layout manager to determine how much
        space to allocate the widget.

        """
        width_hint, height_hint = super(WXTabbed, self).size_hint()
                
        # Compute the size of the tab so we can offset the size hint.
        # On Windows, the return value of the height function is a hard
        # coded default of 20. This is close for the standard font but
        # will probably break down with different fonts or icons. I've
        # found no other way to measure the height of the tab bar.
        tab_size = wx.RendererNative.Get().GetHeaderButtonHeight(self.widget)
        tab_length = self._estimate_tab_bar_length()

        # Offset the size hint by the tab bar size
        style = self.widget.GetWindowStyle()
        if (style & wx.NB_TOP) or (style & wx.NB_BOTTOM):
            height_hint += tab_size
            width_hint = max(width_hint, tab_length)
        else:
            width_hint += tab_size
            height_hint = max(height_hint, tab_length)

        return (width_hint, height_hint)

    def _estimate_tab_bar_length(self):
        """ Estimates the length of the tab bar based on the title text
        of the tab pages. There doesn't seem to be a better wx api for
        getting this information. This is a rough estimate only that was
        empirically determined on Windows 7 using default fonts and does
        account for things like icons or multiline text.

        """
        dc = wx.ClientDC(self.widget)
        f = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        dc.SetFont(f)
        length = 0
        padding = 10
        for child in self.shell_obj.children:
            w, h = dc.GetTextExtent(child.title)
            w = max(w, 35)
            length += w + padding
        return length

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
        self.shell_obj.index = event.GetSelection()

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_index(self, index):
        """ Sets the current index of the tab widget. This is overridden
        from the parent class.

        """
        self.widget.SetSelection(index)
    
    def update_children(self):
        """ Populates the notebook with the child notebook pages. This
        is an overridden parent class method which sets the title of
        of notebook pages properly.

        """
        super(WXTabbed, self).update_children()
        widget = self.widget
        for idx, child in enumerate(self.shell_obj.children):
            widget.SetPageText(idx, child.title)

