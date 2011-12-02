#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_control import QtControl
from .abstract_item_model_wrapper import AbstractItemModelWrapper

from ..tree_view import AbstractTkTreeView


class QtTreeView(QtControl, AbstractTkTreeView):
    """ A Qt implementation of TreeView.

    """
    #: The underlying model.
    model_wrapper = None

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
        self.set_tree_model(self.shell_obj.item_model)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_item_model_changed(self, item_model):
        """ The change handler for the 'item_model' attribute.

        """
        self.set_tree_model(item_model)

    def set_tree_model(self, model):
        """ Set the table view's model.

        """
        model_wrapper = AbstractItemModelWrapper(model)
        self.widget.setModel(model_wrapper)
        self.model_wrapper = model_wrapper

