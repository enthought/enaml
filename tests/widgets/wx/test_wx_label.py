#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_test_assistant import WXTestAssistant
from .. import label

class TestWxLabel(label.TestLabel, WXTestAssistant):
    """ WXLabel tests. """

    def get_text(self, widget):
        """ Get a label's text.

        """
        return widget.GetLabel()
