#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QProgressBar
from .qt_constraints_widget import QtConstraintsWidget


class QtProgressBar(QtConstraintsWidget):
    """ A Qt4 implementation of an Enaml ProgressBar.

    """
    def create(self):
        """ Create the underlying progress bar widget.

        """
        self.widget = QProgressBar(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the widget's attributes.

        """
        super(QtProgressBar, self).initialize(attrs)
        self.set_minimum(attrs['minimum'])
        self.set_maximum(attrs['maximum'])
        self.set_value(attrs['value'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_minimum(self, payload):
        """ Handle the 'set-minimum' action from the Enaml widget.

        """
        self.set_minimum(payload['minimum'])

    def on_message_set_maximum(self, payload):
        """ Handle the 'set-maximum' action from the Enaml widget.

        """
        self.set_maximum(payload['maximum'])

    def on_message_set_value(self, payload):
        """ Handle the 'set-value' action from the Enaml widget.

        """
        self.set_value(payload['value'])

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

