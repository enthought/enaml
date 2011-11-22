#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from .qt_container import QtContainer
from .qt_resizing_widgets import QResizingSplitter

from ..splitter import AbstractTkSplitter


class QtSplitter(QtContainer, AbstractTkSplitter):
    """ Qt implementation of the Splitter Container.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QSplitter control.

        """
        self.widget = QResizingSplitter(self.parent_widget())

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtSplitter, self).initialize()
        self.update_children()

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------

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

    def update_children(self):
        """ Update the QSplitter's children with the current 
        children.

        """
        # FIXME: there should be a more efficient way to do this, but for 
        # now just remove all present widgets and add the current ones.
        widget = self.widget
        while widget.count():
            # FIXME: there is no explicit API to remove a widget from
            # a QSplitter, so we need to do it implicitly by unparenting.
            i = widget.count() - 1
            child = widget.widget(i)
            child.setParent(None)
        shell = self.shell_obj
        for child in shell.children:
            widget.addWidget(child.toolkit_widget)

