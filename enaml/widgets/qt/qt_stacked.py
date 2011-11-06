#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------

from .qt import QtCore
from .qt_container import QtContainer
from .qt_resizing_widgets import QResizingStackedWidget

from ..stacked import AbstractTkStacked


class QtStacked(QtContainer, AbstractTkStacked):
    """ Qt implementation of the Stacked Container.

    """

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------

    def create(self):
        """ Creates the underlying QStackedWidget control.

        """
        self.widget = QResizingStackedWidget(self.parent_widget())

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtStacked, self).initialize()
        self.update_children()

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------

    def shell_index_changed(self, index):
        """ Update the widget index with the new value from the shell object.

        """
        self.widget.setCurrentIndex(index)
        shell = self.shell_obj
        shell.size_hint_updated = True

    def shell_children_changed(self, children):
        """ Update the widget with new children.

        """
        self.update_children()

    def shell_children_items_changed(self, event):
        """ Update the widget with new children.

        """
        self.update_children()
    
    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state. This
        value is used by the layout manager to determine how much
        space to allocate the widget.

        Override to ask the currently displayed widget for its size hint. Fall
        back to the minimum size if there is no size hint. If we use
        a constraints-based Container as a child widget, it will only have
        a minimum size set, not a size hint.

        """
        size_hint = self.widget.currentWidget().sizeHint()
        if not size_hint.isValid():
            size_hint = self.widget.currentWidget().minimumSize()
        return (size_hint.width(), size_hint.height())

    def update_children(self):
        """ Update the QStackedWidget's children with the current children.

        """
        # FIXME: there should be a more efficient way to do this, but for now
        # just remove all present widgets and add the current ones.
        while self.widget.count():
            self.widget.removeWidget(self.widget.currentWidget())
        shell = self.shell_obj
        for child in shell.children:
            self.widget.addWidget(child.toolkit_widget)
        self.shell_index_changed(shell.index)

