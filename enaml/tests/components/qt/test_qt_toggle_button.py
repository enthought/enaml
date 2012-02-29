#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_test_assistant import QtTestAssistant

from .. import toggle_button


class TestQtToggleButton(QtTestAssistant, toggle_button.TestToggleButton):
    """ QtToggleButton tests. 
    
    """
    def get_text(self, widget):
        """ Returns the text from the tookit widget.

        """
        return widget.text()

    def get_checked(self, widget):
        """ Returns the checked status from the tookit widget.

        """
        return widget.isChecked()

    def toggle_button_pressed(self, widget):
        """ Press the toggle button programmatically.

        """
        self.widget.pressed.emit()

    def toggle_button_released(self, widget):
        """ Release the button programmatically.

        """
        self.widget.released.emit()

    def toggle_button_toggle(self, widget):
        """ Toggle the button programmatically.

        """
        self.widget.toggled.emit(True)

