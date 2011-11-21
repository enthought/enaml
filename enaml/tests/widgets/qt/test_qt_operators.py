#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_test_assistant import QtTestAssistant
from .. import operators

class TestQtLessLess(QtTestAssistant, operators.TestLessLess):
    """ TestSuite for the LessLess operator in Qt.

    """
    def get_text(self, widget):
        """ Returns the label text from the tookit widget of Label.

        """
        return widget.text()

    def get_checked(self, widget):
        """ Returns the label text from the tookit widget of CheckBox.

        """
        return widget.isChecked()
