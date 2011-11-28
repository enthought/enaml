#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_control import QtControl
from .abstract_item_model_wrapper import AbstractItemModelWrapper

from ..table_view import AbstractTkTableView


class QtTableView(QtControl, AbstractTkTableView):
    """ A Qt implementation of TableView.

    See Also
    --------
    TableView

    """
    #: The underlying model.
    model_wrapper = None

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Create the underlying QTableView control.

        """
        self.widget = QtGui.QTableView(self.parent_widget())

    def initialize(self):
        """ Initialize the widget with the attributes of this instance.

        """
        super(QtTableView, self).initialize()
        shell = self.shell_obj
        self.set_table_model(shell.item_model)
        self.set_vertical_header_vis(shell.vertical_header_visible)
        self.set_horizontal_header_vis(shell.horizontal_header_visible)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_item_model_changed(self, item_model):
        """ The change handler for the 'item_model' attribute.

        """
        self.set_table_model(item_model)
    
    def shell_vertical_header_visible_changed(self, visible):
        self.set_vertical_header_vis(visible)
    
    def shell_horizontal_header_visible_changed(self, visible):
        self.set_horizontal_header_vis(visible)

    def set_table_model(self, model):
        """ Set the table view's model.

        """
        model_wrapper = AbstractItemModelWrapper(model)
        self.widget.setModel(model_wrapper)
        self.model_wrapper = model_wrapper

    def set_vertical_header_vis(self, visible):
        if visible:
            self.widget.verticalHeader().show()
        else:
            self.widget.verticalHeader().hide()
    
    def set_horizontal_header_vis(self, visible):
        if visible:
            self.widget.horizontalHeader().show()
        else:
            self.widget.horizontalHeader().hide()
        

