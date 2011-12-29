#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from .qt_test_assistant import QtTestAssistant

from .. import selection_models


class QtSelectionTestHelper(object):
    def get_tk_selection(self, widget):
        """ Return the widget's selection as a list of (topleft, botright)
        ranges with (row, col) indexes.

        """
        pysel = []
        for srange in widget.selection():
            topleft = srange.topLeft()
            botright = srange.bottomRight()
            pysel.append(((topleft.row(), topleft.column()), (botright.row(), botright.column())))
        return pysel


class TestQtBaseSelectionModel(QtTestAssistant, QtSelectionTestHelper, selection_models.TestBaseSelectionModel):
    """ QtBaseSelectionModel tests. 

    """

class TestQtRowSelectionModel(QtTestAssistant, QtSelectionTestHelper, selection_models.TestRowSelectionModel):
    """ Qt RowSelectionModel tests. 

    """

