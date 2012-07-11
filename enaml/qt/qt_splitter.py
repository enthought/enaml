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
    """ A Qt4 implementation of an Enaml Splitter.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QSplitter control.

        """
        self.widget = QSplitter(self.parent_widget)

    def initialize(self, attrs):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtSplitter, self).initialize(attrs)
        self.set_orientation(attrs['orientation'])
        self.set_live_drag(attrs['live_drag'])
        self.set_preferred_sizes(attrs['preferred_sizes'])

    #--------------------------------------------------------------------------
    # Message Handler Methods 
    #--------------------------------------------------------------------------
    def on_message_set_orientation(self, payload):
        """ Message handler for set_orientation

        """
        self.set_orientation(payload['orientation'])

    def on_message_set_live_drag(self, payload):
        """ Message handler for set_live_drag

        """
        self.set_live_drag(payload['live_drag'])

    def on_message_set_preferred_sizes(self, payload):
        """ Message handler for set_preferred_sizes

        """
        self.set_preferred_sizes(payload['preferred_sizes'])
    
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

        For sizes not supplied by the user, either via None values or 
        a list which is too short, the current size for that element
        will be used in its place.

        """
        widget = self.widget
        curr_sizes = widget.sizes()[:]
        max_idx = min(len(curr_sizes), len(sizes))
        for idx in xrange(max_idx):
            size = sizes[idx]
            if size is not None:
                curr_sizes[idx] = size
        self.widget.setSizes(curr_sizes)

