#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_toggle_control import QtToggleControl

from ..radio_button import AbstractTkRadioButton


class QtRadioButton(QtToggleControl, AbstractTkRadioButton):
    """ A Qt implementation of RadioButton.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying Qt widget.

        """
        self.widget = QtGui.QRadioButton(parent)

    def bind(self):
        """ Binds the event handlers for the radio button.

        """
        super(QtRadioButton, self).bind()
        widget = self.widget
        widget.toggled.connect(self.on_toggled)
        widget.pressed.connect(self.on_pressed)
        widget.released.connect(self.on_released)

