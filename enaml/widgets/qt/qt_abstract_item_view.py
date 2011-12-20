#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_control import QtControl
from .abstract_item_model_wrapper import AbstractItemModelWrapper

from ..abstract_item_view import AbstractTkItemView


_SELECTION_MODE_MAP = {
    'single': QtGui.QAbstractItemView.SingleSelection,
    'contiguous': QtGui.QAbstractItemView.ContiguousSelection,
    'extended': QtGui.QAbstractItemView.ExtendedSelection,
    'multi': QtGui.QAbstractItemView.MultiSelection,
    'none': QtGui.QAbstractItemView.NoSelection,
}

_SELECTION_BEHAVIOR_MAP = {
    'items' : QtGui.QAbstractItemView.SelectItems,
    'rows' : QtGui.QAbstractItemView.SelectRows,
    'columns' : QtGui.QAbstractItemView.SelectColumns,
}


class QtAbstractItemView(QtControl, AbstractTkItemView):
    """ An abstract base class for implementing Qt item views.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying QItemView control.

        """
        raise NotImplementedError

    def initialize(self):
        """ Initialize the widget with the attributes of this instance.

        """
        super(QtAbstractItemView, self).initialize()
        shell = self.shell_obj
        self.set_item_model(shell.item_model)
        self.set_selection_mode(shell.selection_mode)
        self.set_selection_behavior(shell.selection_behavior)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_item_model_changed(self, item_model):
        """ The change handler for the 'item_model' attribute on the 
        shell object.

        """
        self.set_item_model(item_model)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_item_model(self, item_model):
        """ Sets the model to use for the view.

        """
        model_wrapper = AbstractItemModelWrapper(item_model)
        self.widget.setModel(model_wrapper)

    def set_selection_mode(self, selection_mode):
        """ Sets the selection mode.

        """
        self.widget.setSelectionMode(_SELECTION_MODE_MAP[selection_mode])

    def set_selection_behavior(self, selection_behavior):
        """ Sets the selection behavior.

        """
        self.widget.setSelectionBehavior(_SELECTION_BEHAVIOR_MAP[selection_behavior])

