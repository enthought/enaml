#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt
from .qt.QtGui import QSplitter
from .qt_constraints_widget import QtConstraintsWidget


_ORIENTATION_MAP = {
    'horizontal': Qt.Horizontal,
    'vertical': Qt.Vertical,
}


class QtSplitter(QtConstraintsWidget):
    """ A Qt implementation of a Splitter.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QSplitter control.

        """
        self.widget = QSplitter(self.parent_widget)

    def initialize(self, init_attrs):
        """ Intializes the widget with the attributes of this instance.

        """
        self.set_orientation(init_attrs.get('orientation', 'horizontal'))
        self.set_live_drag(init_attrs.get('live_drag', True))
        self.set_preferred_sizes(init_attrs.get('preferred_sizes', []))

    #--------------------------------------------------------------------------
    # Message Handler Methods 
    #--------------------------------------------------------------------------
    def receive_set_orientation(self, ctxt):
        """ Message handler for set_orientation

        """
        self.set_orientation(ctxt['value'])

    def receive_set_live_drag(self, ctxt):
        """ Message handler for set_live_drag

        """
        self.set_live_drag(ctxt['value'])

    def receive_set_preferred_sizes(self, ctxt):
        """ Message handler for set_preferred_sizes

        """
        self.set_preferred_sizes(ctxt['value'])
    
    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_orientation(self, orientation):
        """ Update the orientation of the QSplitter.

        """
        q_orientation = _ORIENTATION_MAP[orientation]
        self.widget.setOrientation(q_orientation)

    def set_live_drag(self, live_drag):
        """ Update the dragging mode of the QSplitter.

        """
        self.widget.setOpaqueResize(live_drag)

    def set_preferred_sizes(self, sizes):
        """ Set the preferred sizes for the children.

        """
        self.widget.setSizes(sizes)

