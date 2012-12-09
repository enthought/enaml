#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_test_assistant import QtTestAssistant
from .. import progress_bar


class TestQtProgressBar(QtTestAssistant, progress_bar.TestProgressBar):
    """ QtProgressBar tests.
    
    """

    def get_value(self, widget):
        """  Get the toolkits widget's active value.

        """
        return widget.value()

    def get_minimum(self, widget):
        """  Get the toolkits widget's maximum value attribute.

        """
        return widget.minimum()

    def get_maximum(self, widget):
        """ Get the toolkits widget's minimum value attribute.

        """
        return widget.maximum()
