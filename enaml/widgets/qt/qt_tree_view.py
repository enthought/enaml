#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_abstract_item_view import QtAbstractItemView

from ..tree_view import AbstractTkTreeView


class QtTreeView(QtAbstractItemView, AbstractTkTreeView):
    """ A Qt implementation of TreeView.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying QTableView control.

        """
        self.widget = QtGui.QTreeView(parent)

    def initialize(self):
        """ Initialize the widget with the attributes of this instance.

        """
        super(QtTreeView, self).initialize()
        self.set_header_visible(self.shell_obj.header_visible)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_header_visible_changed(self, visible):
        """ The change handler for the 'header_visible' attribute of
        the shell object.

        """
        self.set_header_visible(visible)
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_header_visible(self, visible):
        """ Sets the visibility of the header for the widget.

        """
        if visible:
            self.widget.setHeaderHidden(False)
        else:
            self.widget.setHeaderHidden(True)

