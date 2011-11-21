#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.widgets.qt.qt import QtCore
from .qt_test_assistant import QtTestAssistant
from .. import group_box

# The alignment object we get back from widget.alignment() is not
# hashable. So we convert the flags to ints.
QT_2_ENAML_ALIGNMENTS = {int(QtCore.Qt.AlignLeft): 'left',
                         int(QtCore.Qt.AlignRight): 'right',
                         int(QtCore.Qt.AlignHCenter): 'center'}


class TestGroupBox(QtTestAssistant, group_box.TestGroupBox):

    def get_title(self, component, widget):
        """ Returns the title text from the tookit widget

        """
        return widget.title()

    def get_flat(self, component, widget):
        """ Returns the flat style status from the tookit widget

        """
        return widget.isFlat()

    def get_title_align(self, component, widget):
        """ Returns the title aligment in the tookit widget

        """
        alignment = int(widget.alignment())
        return QT_2_ENAML_ALIGNMENTS[alignment]