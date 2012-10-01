#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt
from .qt.QtGui import QSplitter
from .qt_constraints_widget import QtConstraintsWidget
from .qt_container import QtContainer


_ORIENTATION_MAP = {
    'horizontal': Qt.Horizontal,
    'vertical': Qt.Vertical,
}


class QtSplitter(QtConstraintsWidget):
    """ A Qt implementation of an Enaml Splitter.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying QSplitter control.

        """
        return QSplitter(parent)

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(QtSplitter, self).create(tree)
        self.set_orientation(tree['orientation'])
        self.set_live_drag(tree['live_drag'])
        self.set_preferred_sizes(tree['preferred_sizes'])

    def init_layout(self):
        """ Handle the layout initialization for the splitter.

        """
        super(QtSplitter, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, QtContainer):
                widget.addWidget(child.widget())

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtSplitter.

        """
        if isinstance(child, QtContainer):
            self.widget().addWidget(child.widget())
            self.size_hint_updated()

    #--------------------------------------------------------------------------
    # Message Handler Methods 
    #--------------------------------------------------------------------------
    def on_action_set_orientation(self, content):
        """ Handle the 'set_orientation' action from the Enaml widget.

        """
        self.set_orientation(content['orientation'])

    def on_action_set_live_drag(self, content):
        """ Handle the 'set_live_drag' action from the Enaml widget.

        """
        self.set_live_drag(content['live_drag'])

    def on_action_set_preferred_sizes(self, content):
        """ Handle the 'set_preferred_sizes' action from the Enaml 
        widget.

        """
        self.set_preferred_sizes(content['preferred_sizes'])
    
    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_orientation(self, orientation):
        """ Update the orientation of the QSplitter.

        """
        q_orientation = _ORIENTATION_MAP[orientation]
        self.widget().setOrientation(q_orientation)

    def set_live_drag(self, live_drag):
        """ Update the dragging mode of the QSplitter.

        """
        self.widget().setOpaqueResize(live_drag)

    def set_preferred_sizes(self, sizes):
        """ Set the preferred sizes for the children.

        For sizes not supplied by the user, either via None values or 
        a list which is too short, the current size for that element
        will be used in its place.

        """
        widget = self.widget()
        curr_sizes = widget.sizes()[:]
        max_idx = min(len(curr_sizes), len(sizes))
        for idx in xrange(max_idx):
            size = sizes[idx]
            if size is not None:
                curr_sizes[idx] = size
        widget.setSizes(curr_sizes)

