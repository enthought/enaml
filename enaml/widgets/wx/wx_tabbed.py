#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_container import WXContainer

from ..tabbed import AbstractTkTabbed


#: A mapping from TabPosition enum values to qt tab positions.
_TAB_POSITION_MAP = {
    'top': wx.NB_TOP,
    'bottom': wx.NB_BOTTOM,
    'left': wx.NB_LEFT,
    'right': wx.NB_RIGHT,
}


# Notice we are not subclassing from WXStacked here because the internals
# need to be handled drastically differently due to limitations of the
# wxNotebook.
class WXTabbed(WXContainer, AbstractTkTabbed):
    """ A wx implementation of the Tabbed container.

    """
    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def create(self):
        """ Create the underlying QTabWidget control.

        """
        # Changing the tab position of the notebook dynamically is not
        # supported by wx. So in order to do this we need to rebuild 
        # the entire notebook whenever the orientation of the tabs change.
        # So, we initially create a notebook here just our children will
        # have a parent to use, but everything is really handled by the 
        # _rebuild_nb method().
        self.widget = wx.Notebook(self.parent_widget())

    def bind(self):
        """ Bind to the events emitted by the underlying control.

        """
        # Because of limitations in the wx.Notebook control and how it
        # handles changing the orientation of the tab bar dynamically,
        # we just rebuild it as the last part of the layout setup
        # process.
        super(WXTabbed, self).bind()
        self._rebuild_nb()

    #--------------------------------------------------------------------------
    # Implementation 
    #--------------------------------------------------------------------------
    def shell_index_changed(self, index):
        """ The change handler for the 'index' attribute of the shell 
        object.

        """
        self._set_index(index)
        self.shell_obj.size_hint_updated = True

    def shell_children_changed(self, children):
        """ Update the widget with new children.

        """
        # It's easiest to just rebuild the notebook
        self._rebuild_nb()

    def shell_children_items_changed(self, event):
        """ Update the widget with new children.

        """
        # It's easiest to just rebuild the notebook
        self._rebuild_nb()

    def shell_tab_position_changed(self, tab_position):
        """ The change handler for the 'tab_position' attribute of the
        shell object.

        """
        self._set_tab_position(tab_position)

    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state. This
        value is used by the layout manager to determine how much
        space to allocate the widget.

        Override to add the content margins to the size hint.

        """
        return (256, 192)

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
    def _set_tab_position(self, tab_position):
        """ Sets the position of the tabs on the underlying tab widget.

        """        
        # The notebook needs to be rebuilt to reliably change the tab
        # position.
        self._rebuild_nb()

    def _set_index(self, index):
        """ Sets the current index of the tab widget. This is overridden
        from the parent class.

        """
        self.widget.SetSelection(index)
    
    def _rebuild_nb(self):
        """ Performs the actual create/initialize/bind of the widget.

        """
        # First remove all the old pages from the existing notebook.
        shell = self.shell_obj
        old_widget = self.widget
        while old_widget.GetPageCount():
            old_widget.RemovePage(0)

        # Grab the position that tabs should be in (this is the 
        # only style flag needed for the notebook) and create the 
        # new notebook widget.
        pos = _TAB_POSITION_MAP[shell.tab_position]
        new_widget = wx.Notebook(self.parent_widget(), style=pos)

        # Reparent all of the child widgets to the new notebook.
        for child in shell.children:
            child_widget = child.toolkit_widget
            child_widget.Reparent(new_widget)
            new_widget.AddPage(child_widget, child.title)

        # Give the parent classes a chance to initialize and bind 
        # the new notebook.
        self.initialize()
        super(WXTabbed, self).bind()

        # Perform our necessary binding for the notebook changed handler.
        new_widget.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_page_changed)

        # Finally, destory the old widget and switch to the current page.
        self.widget = new_widget
        old_widget.Destroy()
        self._set_index(shell.index)
        new_widget.Refresh()
        shell.set_needs_update_constraints()
