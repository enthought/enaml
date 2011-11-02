#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from . import test_qt_window
from .. import dialog

class TestQtDialog(test_qt_window.TestQtWindow, dialog.TestDialog):
    """ QtDialog tests. """

    def get_result(self, widget):
        """ Get the result value from the widget.

        """
        qt_result = widget.result()
        if qt_result == widget.Accepted:
            return 'accepted'
        elif qt_result == widget.Rejected:
            return 'rejected'
        else:
            return qt_result
