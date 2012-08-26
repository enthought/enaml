#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QMdiArea
from .qt_constraints_widget import QtConstraintsWidget


class QtMdiArea(QtConstraintsWidget):
    """ A Qt implementation of an Enaml MdiArea.

    """
    #: Storage for the mdi window ids.
    _mdi_window_ids = []

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QMdiArea widget.

        """
        return QMdiArea(parent)

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(QtMdiArea, self).create(tree)
        self.set_mdi_window_ids(tree['mdi_window_ids'])

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtMdiArea, self).init_layout()
        widget = self.widget()
        find_child = self.find_child
        for window_id in self._mdi_window_ids:
            child = find_child(window_id)
            if child is not None:
                widget.addSubWindow(child.widget())

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_mdi_window_ids(self, window_ids):
        """ Set the widget ids for the mdi windows.

        """
        self._mdi_window_ids = window_ids

