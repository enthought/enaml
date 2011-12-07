#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_abstract_item_view import QtAbstractItemView

from ..list_view import AbstractTkListView


class QtListView(QtAbstractItemView, AbstractTkListView):
    """ A Qt implementation of ListView.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying QTableView control.

        """
        self.widget = QtGui.QListView(parent)

