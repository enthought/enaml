#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_test_assistant import WXTestAssistant
from .. import operators

class TestWXLessLess(WXTestAssistant, operators.TestLessLess):
    """ TestSuite for the LessLess operator in WX.

    """
    def get_text(self, widget):
        """ Returns the label text from the tookit widget of Label.

        """
        return widget.GetLabel()

    def get_checked(self, widget):
        """ Returns the label text from the tookit widget of CheckBox.

        """
        return widget.GetValue()
