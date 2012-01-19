#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtCore, QtGui
from .qt_layout_component import QtLayoutComponent

from ..splitter import AbstractTkSplitter


_ORIENTATION_MAP = {
    'horizontal': QtCore.Qt.Horizontal,
    'vertical': QtCore.Qt.Vertical,
}


class QtSplitter(QtLayoutComponent, AbstractTkSplitter):
    """ A Qt implementation of a Splitter.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QSplitter control.

        """
        self.widget = QtGui.QSplitter(parent)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtSplitter, self).initialize()
        shell = self.shell_obj
        self.set_orientation(shell.orientation)
        self.set_live_drag(shell.live_drag)
        self.update_children()

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_orientation_changed(self, orientation):
        """ Update the orientation of the widget.

        """
        self.set_orientation(orientation)

    def shell_live_drag_changed(self, live_drag):
        """ The change handler for the 'live_drag' attribut of the shell
        object.

        """
        self.set_live_drag(live_drag)

    def shell_layout_children_changed(self, children):
        """ The change handler for the 'layout_children' attribute of 
        the shell object.

        """
        self.update_children()
    
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
        
    def update_children(self):
        """ Update the QSplitter's children with the current 
        children.

        """
        # FIXME: there should be a more efficient way to do this, but for 
        # now just remove all present widgets and add the current ones.
        widget = self.widget
        while widget.count():
            # FIXME: there is no explicit API to remove a widget from
            # a QSplitter, so we need to do it implicitly by unparenting.
            i = widget.count() - 1
            child = widget.widget(i)
            child.setParent(None)
        shell = self.shell_obj
        for child in shell.layout_children:
            widget.addWidget(child.toolkit_widget)

    def set_splitter_sizes(self, sizes):
        """ Set the initial sizes for the children.

        """
        self.widget.setSizes(sizes)

