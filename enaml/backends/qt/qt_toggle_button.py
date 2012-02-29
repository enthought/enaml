#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_toggle_control import QtToggleControl

from ...components.toggle_button import AbstractTkToggleButton


class QtToggleButton(QtToggleControl, AbstractTkToggleButton):
    """ A Qt implementation of ToggleButton.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QPushButton control which has the 
        'checkable' property set to True.

        """
        self.widget = QtGui.QPushButton(parent)
        # The QPushButton is not toggleable until it is 'setCheckable'. 
        # It must be toggleable before 'QtToggleControl.initialize' is 
        # called, so we do that here.
        self.widget.setCheckable(True)
        
    def bind(self):
        """ Binds the event handlers for the toggle button.

        """
        super(QtToggleButton, self).bind()
        widget = self.widget
        widget.toggled.connect(self.on_toggled)
        widget.pressed.connect(self.on_pressed)
        widget.released.connect(self.on_released)
        
