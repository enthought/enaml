#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_layout_component import QtLayoutComponent

from ..tab_group import AbstractTkTabGroup


#: A mapping from TabPosition enum values to qt tab positions.
_TAB_POSITION_MAP = {
    'top': QtGui.QTabWidget.North,
    'bottom': QtGui.QTabWidget.South,
    'left': QtGui.QTabWidget.West,
    'right': QtGui.QTabWidget.East,
}


class QtTabGroup(QtLayoutComponent, AbstractTkTabGroup):
    """ A Qt implementation of TabGroup.

    """
    # Simpilar to QtGroupBox, don't use a widget item to compute layout
    # geometry, or layouts dont get enough space between other controls
    # and the tab widget.
    use_widget_item_for_layout = False

    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying QTabWidget control.

        """
        self.widget = QtGui.QTabWidget(parent)

    def initialize(self):
        """ Initialize the attributes of the QTabWidget.

        """
        super(QtTabGroup, self).initialize()
        self.update_tabs()
        shell = self.shell_obj
        self.set_selected_index(shell.selected_index)
        self.set_tab_position(shell.tab_position)

    def bind(self):
        """ Bind to the events emitted by the underlying control.

        """
        super(QtTabGroup, self).bind()
        self.widget.currentChanged.connect(self._on_current_changed)

    #--------------------------------------------------------------------------
    # Abstract Implementation 
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
        self.set_tab_position(tab_position)

    def shell_selected_index_changed(self, index):
        """ Update the widget index with the new value from the shell 
        object.

        """
        self.set_selected_index(index)

    #--------------------------------------------------------------------------
    # Event Handlers 
    #--------------------------------------------------------------------------
    def _on_current_changed(self):
        """ The event handler for the 'currentChanged' signal of the 
        underlying control. Synchronizes the index of the shell object.

        """
        self.shell_obj._selected_index = self.widget.currentIndex()

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_tab_position(self, tab_position):
        """ Sets the position of the tabs on the underlying tab widget.

        """
        q_tab_position = _TAB_POSITION_MAP[tab_position]
        self.widget.setTabPosition(q_tab_position)

    def set_selected_index(self, index):
        """ Sets the current index of the tab widget. This is overridden
        from the parent class.

        """
        self.widget.setCurrentIndex(index)

    def update_tabs(self):
        """ Update the QTabWidget's children with the current children.
        This is an overridden parent class method.

        """
        widget = self.widget
        widget.clear()
        old_idx = widget.currentIndex()
        for tab in self.shell_obj.tabs:
            widget.addTab(tab.toolkit_widget, tab.title)
        widget.setCurrentIndex(old_idx)

