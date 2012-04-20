#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest
from . import test_wx_window
from .. import dialog


@unittest.skip('Wx Dialog must be run in an event loop to work')
class TestWXDialog(test_wx_window.TestWXWindow, dialog.TestDialog):
    """ WXDialog tests. """

    def get_title(self, widget):
        """ Get a window's title.

        """
        return widget.GetTitle()

    def disable_showing(self, widget):
        """ Disable the actual display of the dialog window.

        """
        widget.ShowModal = lambda:None


