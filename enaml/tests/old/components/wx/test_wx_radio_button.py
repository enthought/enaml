#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_test_assistant import WXTestAssistant, skip_nonwindows
from .. import radio_button


@skip_nonwindows
class TestWxRadioButton(WXTestAssistant, radio_button.TestRadioButton):
    """ WXRadioButton tests. """

    def get_value(self, button):
        """ Get the checked state of a radio button.

        """
        self.process_wx_events(self.app)
        return button.GetValue()

    def get_text(self, button):
        """ Get the label of a button.

        """
        return button.GetLabel()
