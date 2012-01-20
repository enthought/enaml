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

    def bind(self):
        """ Bind any event/signal handlers for the Qt Widget.

        """
        super(QtAbstractItemView, self).bind()
        widget = self.toolkit_widget
        widget.activated.connect(lambda idx: self._send_event(idx, 'activated'))
        widget.clicked.connect(lambda idx: self._send_event(idx, 'clicked'))
        widget.doubleClicked.connect(lambda idx: self._send_event(idx, 'double_clicked'))

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
        # Save the model wrapper. PySide's object cache is sometimes unreliable
        # in various versions.
        self.model_wrapper = AbstractItemModelWrapper(item_model)
        self.widget.setModel(self.model_wrapper)

    #--------------------------------------------------------------------------
    # Event notification methods
    #--------------------------------------------------------------------------
    def _send_event(self, qindex, trait):
        """ Send a ModelIndex to the given shell trait.

        """
        model = self.model_wrapper
        index = model.from_q_index(qindex)
        getattr(self.shell_obj, trait)(index)
