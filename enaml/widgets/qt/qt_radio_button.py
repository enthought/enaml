#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui

from traits.api import implements

from .qt_toggle_control import QtToggleControl

from ..radio_button import IRadioButtonImpl


class QtRadioButton(QtToggleControl):
    """ A Qt implementation of RadioButton.

    See Also
    --------
    RadioButton

    """
    implements(IRadioButtonImpl)

    #---------------------------------------------------------------------------
    # IRadioButtonImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        self.widget = QtGui.QRadioButton(self.parent_widget())
        
    def bind(self):
        """ Binds the event handlers for the radio button. Not meant for
        public consumption.

        """
        widget = self.widget
        widget.toggled.connect(self.on_toggled)
        widget.pressed.connect(self.on_pressed)
        widget.released.connect(self.on_released)
    
