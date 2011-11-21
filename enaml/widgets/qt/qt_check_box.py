#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui

from .qt_toggle_control import QtToggleControl

from ..check_box import AbstractTkCheckBox


class QtCheckBox(QtToggleControl, AbstractTkCheckBox):
    """ A Qt implementation of CheckBox.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QCheckBox widget.

        """
        self.widget = QtGui.QCheckBox(self.parent_widget())
        
    def bind(self):
        """ Binds the event handlers for the check box.

        """
        super(QtCheckBox, self).bind()
        widget = self.widget
        widget.toggled.connect(self.on_toggled)
        widget.pressed.connect(self.on_pressed)
        widget.released.connect(self.on_released)
        
