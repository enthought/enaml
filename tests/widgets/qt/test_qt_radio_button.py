#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_test_assistant import QtTestAssistant
from .. import radio_button


class TestQtRadioButton(QtTestAssistant, radio_button.TestRadioButton):
    """ QtRadioButton tests. """

    def get_value(self, button):
        """ Get the checked state of a radio button.

        """
        return button.isChecked()

    def get_text(self, button):
        """ Get the label of a button.

        """
        return button.text()

