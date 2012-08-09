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
        self.widget.setTextVisible(False)
        
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
    def on_action_set_minimum(self, content):
        """ Handle the 'set_minimum' action from the Enaml widget.

        """
        self.set_minimum(content['minimum'])

    def on_action_set_maximum(self, content):
        """ Handle the 'set_maximum' action from the Enaml widget.

        """
        self.set_maximum(content['maximum'])

    def on_action_set_value(self, content):
        """ Handle the 'set_value' action from the Enaml widget.

        """
        self.set_value(content['value'])

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

