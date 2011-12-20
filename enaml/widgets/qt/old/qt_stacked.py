#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from .qt_container import QtContainer
from .qt_resizing_widgets import QResizingStackedWidget

from ..stacked import AbstractTkStacked


class QtStacked(QtContainer, AbstractTkStacked):
    """ Qt implementation of the Stacked Container.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QStackedWidget control.

        """
        self.widget = QResizingStackedWidget(parent)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtStacked, self).initialize()
        self.update_children()
        self.set_index(self.shell_obj.index)

        # XXX Temporary hack to overcome some visibility issues
        # during initialization.
        idx = self.shell_obj.index
        for i, child in enumerate(self.shell_obj.children):
            if idx != i:
                child.visible = False
    
    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_index_changed(self, index):
        """ Update the widget index with the new value from the shell 
        object.

        """
        self.set_index(index)
        self.shell_obj.size_hint_updated = True

    def shell_children_changed(self, children):
        """ Update the widget with new children.

        """
        self.update_children()

    def shell_children_items_changed(self, event):
        """ Update the widget with new children.

        """
        self.update_children()
    
    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_index(self, index):
        """ Set the current visible index of the widget.

        """
        self.widget.setCurrentIndex(index)

    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state. This
        value is used by the layout manager to determine how much
        space to allocate the widget.

        Override to ask the currently displayed widget for its size hint. 
        Fall back to the minimum size if there is no size hint. If we use
        a constraints-based Container as a child widget, it will only have
        a minimum size set, not a size hint.

        """
        shell = self.shell_obj
        curr_shell = shell.children[shell.index]
        size_hint = curr_shell.size_hint()
        if size_hint == (-1, -1):
            q_size = curr_shell.toolkit_widget.minimumSize()
            size_hint = (q_size.width(), q_size.height())
        print 'size hint', size_hint
        return size_hint

    def update_children(self):
        """ Update the QStackedWidget's children with the current 
        children.

        """
        # FIXME: there should be a more efficient way to do this, but for 
        # now just remove all present widgets and add the current ones.
        shell = self.shell_obj
        widget = self.widget
        while widget.count():
            widget.removeWidget(widget.currentWidget())

        # Reparent all of the child widgets to the new parent.
        for child in shell.children:
            widget.addWidget(child.toolkit_widget)

        # Finally, update the selected index of the of the widget 
        # and notify the layout of the size hint update
        self.set_index(shell.index)

