#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ..common import label
from enaml.toolkit import qt_toolkit

class TestQtLabel(label.TestLabel):
    """ QtLabel tests. """

    toolkit = qt_toolkit()

    def get_text(self, widget):
        """ Get a label's text.

        """
        return widget.text()
