#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui

from .qt_stacked import QtStacked
from .qt_resizing_widgets import QResizingTabWidget

from ..tabbed import AbstractTkTabbed


#: A mapping from TabPosition enum values to qt tab positions.
_TAB_POSITION_MAP = {
    'top': QtGui.QTabWidget.North,
    'bottom': QtGui.QTabWidget.South,
    'left': QtGui.QTabWidget.West,
    'right': QtGui.QTabWidget.East,
}


class QtTabbed(QtStacked, AbstractTkTabbed):
    """ A Qt implementation of the Tabbed container.

    """
    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def create(self):
        """ Create the underlying QTabWidget control.

        """
        self.widget = QResizingTabWidget(self.parent_widget())

    def initialize(self):
        """ Initialize the attributes of the Tabbed container.

        """
        super(QtTabbed, self).initialize()
        self._set_tab_position(self.shell_obj.tab_position)

    def bind(self):
        """ Bind to the events emitted by the underlying control.

        """
        super(QtTabbed, self).bind()
        self.widget.currentChanged.connect(self._on_current_changed)

    #--------------------------------------------------------------------------
    # Implementation 
    #--------------------------------------------------------------------------
    def shell_tab_position_changed(self, tab_position):
        """ The change handler for the 'tab_position' attribute of the
        shell object.

        """
        self._set_tab_position(tab_position)

    #--------------------------------------------------------------------------
    # Event Handlers 
    #--------------------------------------------------------------------------
    def _on_current_changed(self):
        """ The event handler for the 'currentChanged' signal of the 
        underlying control. Synchronizes the index of the shell object.

        """
        self.shell_obj.index = self.widget.currentIndex()

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def _set_tab_position(self, tab_position):
        """ Sets the position of the tabs on the underlying tab widget.

        """
        q_tab_position = _TAB_POSITION_MAP[tab_position]
        self.widget.setTabPosition(q_tab_position)

    def set_index(self, index):
        """ Sets the current index of the tab widget. This is overridden
        from the parent class.

        """
        self.widget.setCurrentIndex(index)

    def update_children(self):
        """ Update the QTabWidget's children with the current children.
        This is an overridden parent class method.

        """
        shell = self.shell_obj
        widget = self.widget
        widget.clear()
        for child in shell.children:
            widget.addTab(child.toolkit_widget, child.title)
        self.set_index(shell.index)

