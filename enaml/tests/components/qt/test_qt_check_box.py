#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_test_assistant import QtTestAssistant
from .. import check_box

class TestQtCheckBox(QtTestAssistant, check_box.TestCheckBox):
    """ QtCheckbox tests. """

    def get_text(self, widget):
        """ Returns the text from the tookit widget.

        """
        return widget.text()

    def get_checked(self, widget):
        """ Returns the checked status from the tookit widget.

        """
        return widget.isChecked()

    def checkbox_pressed(self, widget):
        """ Press the checkbox programmatically.

        """
        self.widget.pressed.emit()

    def checkbox_released(self, widget):
        """ Release the button programmatically.

        """
        self.widget.released.emit()

    def checkbox_toggle(self, widget):
        """ Toggle the button programmatically.

        """
        self.widget.toggled.emit(True)
