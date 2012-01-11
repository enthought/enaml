#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_abstract_item_view import QtAbstractItemView

from ..table_view import AbstractTkTableView


class QtTableView(QtAbstractItemView, AbstractTkTableView):
    """ A Qt implementation of TableView.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying QTableView control.

        """
        self.widget = QtGui.QTableView(parent)

    def initialize(self):
        """ Initialize the widget with the attributes of this instance.

        """
        super(QtTableView, self).initialize()
        shell = self.shell_obj
        self.set_vertical_header_visible(shell.vertical_header_visible)
        self.set_horizontal_header_visible(shell.horizontal_header_visible)

    #--------------------------------------------------------------------------
    # Implementation
    #-------------------------------------------------------------------------- 
    def shell_vertical_header_visible_changed(self, visible):
        """ The change handler for the 'vertical_header_visible' 
        attribute of the shell object.

        """
        self.set_vertical_header_visible(visible)
    
    def shell_horizontal_header_visible_changed(self, visible):
        """ The change handler for the 'horizontal_header_visible'
        attribute of the shell object.

        """
        self.set_horizontal_header_visible(visible)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_vertical_header_visible(self, visible):
        """ Sets the vertical header visibility of the widget.

        """
        if visible:
            self.widget.verticalHeader().show()
        else:
            self.widget.verticalHeader().hide()
    
    def set_horizontal_header_visible(self, visible):
        """ Sets the horizontal header visibility of the widget.

        """
        if visible:
            self.widget.horizontalHeader().show()
        else:
            self.widget.horizontalHeader().hide()

