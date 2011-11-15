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
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QProgressBar.

        """
        self.widget = QtGui.QProgressBar(self.parent_widget())
    
    def initialize(self):
        super(QtControl, self).initialize()
        self.widget.setTextVisible(False)
        shell = self.shell_obj
        self.shell_minimum_changed(shell.minimum)
        self.shell_maximum_changed(shell.maximum)
        self.shell_value_changed(shell.value)

    #--------------------------------------------------------------------------
    # Abstract implementation methods
    #--------------------------------------------------------------------------
    def shell_value_changed(self, value):
        self.widget.setValue(value)

    def shell_minimum_changed(self, minimum):
        self.widget.setMinimum(minimum)
    
    def shell_maximum_changed(self, maximum):
        self.widget.setMaximum(maximum)

