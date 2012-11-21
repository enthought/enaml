#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_test_assistant import QtTestAssistant
from .. import html

class TestQtHtml(QtTestAssistant, html.TestHtml):
    """ QtHtml tests. """

    def get_source(self, widget):
        """ Get the source of an Html widget.

        """
        return widget.toPlainText()
