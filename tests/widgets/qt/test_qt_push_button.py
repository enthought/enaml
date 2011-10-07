#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_test_assistant import QtTestAssistant
from .. import push_button


class TestQtPushButton(QtTestAssistant, push_button.TestPushButton):
    """ QtPushButton tests. """

    def button_pressed(self):
        """ Press the button programmatically.

        """
        self.widget.pressed.emit()

    def button_released(self):
        """ Release the button programmatically.

        """
        self.widget.released.emit()

    def button_clicked(self):
        """ Click the button programmatically.

        PySide expects 0 arguments for this signal, but PyQt expects 1.

        """
        try:
            self.widget.clicked.emit(False)
        except TypeError:
            self.widget.clicked.emit()
