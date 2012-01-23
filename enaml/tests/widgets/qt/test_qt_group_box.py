#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from unittest import expectedFailure

from enaml.widgets.qt.qt import QtCore
from .qt_test_assistant import QtTestAssistant
from .. import group_box

# The alignment object we get back from widget.alignment() is not
# hashable. So we convert the flags to ints.
QT_2_ENAML_ALIGNMENTS = {int(QtCore.Qt.AlignLeft): 'left',
                         int(QtCore.Qt.AlignRight): 'right',
                         int(QtCore.Qt.AlignHCenter): 'center'}


class TestQtGroupBox(QtTestAssistant, group_box.TestGroupBox):

    # This test is an expected failure since calling process
    # events on qt still doesn't seem to empty the relayout
    # queue which has call-later events waiting. Without
    # those being processed, the title update never happens.
    @expectedFailure
    def test_title_changed(self):
        super(TestGroupBox, self).test_title_changed(self)

    def get_title(self, component, widget):
        """ Returns the title text from the tookit widget

        """
        # The title is set on a deferred call, so we need to pump
        # the event loop a bit to get the title to change.
        # XXX this doesn't work, see above comment.
        self.toolkit.app.process_events()
        return widget.title()

    # This test is an expected failure since calling process
    # events on qt still doesn't seem to empty the relayout
    # queue which has call-later events waiting. Without
    # those being processed, the flat update never happens.
    @expectedFailure
    def test_flat_style_changed(self):
        super(TestGroupBox, self).test_flat_style_changed(self)

    def get_flat(self, component, widget):
        """ Returns the flat style status from the tookit widget

        """
        # The flat is set on a deferred call, so we need to pump
        # the event loop a bit to get the title to change.
        # XXX this doesn't work, see above comment.
        self.toolkit.app.process_events()
        return widget.isFlat()

    def get_title_align(self, component, widget):
        """ Returns the title aligment in the tookit widget

        """
        alignment = int(widget.alignment())
        return QT_2_ENAML_ALIGNMENTS[alignment]