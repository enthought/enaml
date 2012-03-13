#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_test_assistant import WXTestAssistant, skip_nonwindows
from .. import window

@skip_nonwindows
class TestWXWindow(WXTestAssistant, window.TestWindow):
    """ WXWindow tests. """

    def get_title(self, widget):
        """ Get a window's title.

        """
        return widget.GetTitle()

