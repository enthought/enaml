#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QProgressBar
from .qt_constraints_widget import QtConstraintsWidget

class QtProgressBar(QtConstraintsWidget):
    """ An progress bar based on a QProgressBar

    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = QProgressBar(self.parent_widget)

    def initialize(self, init_attrs):
        """ Initialize the widget's attributes

        """
        super(QtProgressBar, self).initialize(init_attrs)
        self.set_minimum(init_attrs.get('minimum', 0))
        self.set_maximum(init_attrs.get('maximum', 100))
        self.set_value(init_attrs.get('value', 0))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_minimum(self, ctxt):
        """ Message handler for set_minimum

        """
        minimum = ctxt.get('minimum')
        if minimum is not None:
            self.set_minimum(minimum)

    def receive_set_maximum(self, ctxt):
        """ Message handler for set_maximum

        """
        maximum = ctxt.get('maximum')
        if maximum is not None:
            self.set_maximum(maximum)

    def receive_set_value(self, ctxt):
        """ Message handler for set_value

        """
        value = ctxt.get('value')
        if value is not None:
            self.set_value(value)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_minimum(self, value):
        """ Set the minimum value of the progress bar

        """
        self.widget.setMinimum(value)

    def set_maximum(self, value):
        """ Set the maximum value of the progress bar

        """
        self.widget.setMaximum(value)

    def set_value(self, value):
        """ Set the value of the progress bar

        """
        self.widget.setValue(value)
