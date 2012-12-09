#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from . import test_qt_window
from .. import dialog

class TestQtDialog(test_qt_window.TestQtWindow, dialog.TestDialog):
    """ QtDialog tests. """

    def disable_showing(self, widget):
        """ Disable the actual display of the dialog window.

        """
        widget.exec_ = lambda:None
        widget.show = lambda:None
        widget.setWindowModality = lambda x:None

