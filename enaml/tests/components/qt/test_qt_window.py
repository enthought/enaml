#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_test_assistant import QtTestAssistant
from .. import window

class TestQtWindow(QtTestAssistant, window.TestWindow):
    """ QtWindow tests. """

    def get_title(self, widget):
        """ Get a window's title.

        """
        return widget.windowTitle()

