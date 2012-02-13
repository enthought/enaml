#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_control import QtControl
from .qt import QtGui

from ..progress_bar import AbstractTkProgressBar


class QtProgressBar(QtControl, AbstractTkProgressBar):
    """ Qt implementation of ProgressBar.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QProgressBar.

        """
        self.widget = QtGui.QProgressBar(parent)
    
    def initialize(self):
        """ Initialize the attributes of the progress bar.

        """
        super(QtControl, self).initialize()
        self.widget.setTextVisible(False)
        shell = self.shell_obj
        self._set_minimum(shell.minimum)
        self._set_maximum(shell.maximum)
        self._set_value(shell.value)

    #--------------------------------------------------------------------------
    # Abstract Implementation Methods
    #--------------------------------------------------------------------------
    def shell_value_changed(self, value):
        """ The change handler for the 'value' attribute of the shell
        object.

        """
        self._set_value(value)

    def shell_minimum_changed(self, minimum):
        """ The change handler for the 'minimum' attribute of the shell
        object.

        """
        self._set_minimum(minimum)
            
    def shell_maximum_changed(self, maximum):
        """ The change handler for the 'maximum' attribute of the shell
        object

        """
        self._set_maximum(maximum)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def _set_value(self, value):
        """ Sets the value of the progress bar.

        """
        self.widget.setValue(value)

    def _set_minimum(self, minimum):
        """ Sets the minimum value of the progress bar.

        """
        self.widget.setMinimum(minimum)
    
    def _set_maximum(self, maximum):
        """ Sets the maximum value of the progress bar.

        """
        self.widget.setMaximum(maximum)

