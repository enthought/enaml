#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_test_assistant import QtTestAssistant
from .. import label

class TestQtLabel(QtTestAssistant, label.TestLabel):
    """ QtLabel tests. """

    def get_text(self, widget):
        """ Get a label's text.

        """
        return widget.text()
