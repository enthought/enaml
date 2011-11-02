#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ....widgets.qt.qt import QtCore
from .qt_test_assistant import QtTestAssistant
from .. import window

class TestQtWindow(QtTestAssistant, window.TestWindow):
    """ QtWindow tests. """

    def get_title(self, widget):
        """ Get a window's title.

        """
        return widget.windowTitle()

    def get_modality(self, widget):
        """ Get a window's modality.

        """
        qt_modality = widget.windowModality()
        if qt_modality == QtCore.Qt.ApplicationModal:
            return 'app_modal'
        elif qt_modality == QtCore.Qt.WindowModal:
            return 'modal'
        elif qt_modality == QtCore.Qt.NonModal:
            return 'non_modal'
        else:
            # Just return the Qt object itself and let the test fail.
            return qt_modality

