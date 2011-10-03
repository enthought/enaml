#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .. import html
from enaml.toolkit import qt_toolkit


class TestQtHtml(html.TestHtml):
    """ QtHtml tests. """

    toolkit = qt_toolkit()

    def get_source(self, widget):
        """ Get the source of an Html widget.

        """
        return widget.toPlainText()
