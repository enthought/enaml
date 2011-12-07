#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_control import QtControl
from .abstract_item_model_wrapper import AbstractItemModelWrapper

from ..abstract_item_view import AbstractTkItemView


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
        self.set_selection_model(shell.selection_model)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_item_model_changed(self, item_model):
        """ The change handler for the 'item_model' attribute on the 
        shell object.

        """
        self.set_item_model(item_model)
    
    def shell_selection_model_changed(self, selection_model):
        """ The change handler for the 'selection_model' attribute on
        the shell object.

        """
        self.set_selection_model(selection_model)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_item_model(self, item_model):
        """ Sets the model to use for the view.

        """
        model_wrapper = AbstractItemModelWrapper(item_model)
        self.widget.setModel(model_wrapper)
    
    def set_selection_model(self, selection_model):
        """ Sets the selection model to use for the view.

        """
        # Selection models are not yet implemented
        pass

