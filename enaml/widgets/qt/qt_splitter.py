#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtCore
from .qt_container import QtContainer
from .qt_resizing_widgets import QResizingSplitter

from ..splitter import AbstractTkSplitter


_ORIENTATION_MAP = {
    'horizontal': QtCore.Qt.Horizontal,
    'vertical': QtCore.Qt.Vertical,
}


class QtSplitter(QtContainer, AbstractTkSplitter):
    """ Qt implementation of the Splitter Container.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QSplitter control.

        """
        self.widget = QResizingSplitter(self.parent_widget())

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

    def shell_children_changed(self, children):
        """ Update the widget with new children.

        """
        self.update_children()

    def shell_children_items_changed(self, event):
        """ Update the widget with new children.

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
        for child in shell.children:
            widget.addWidget(child.toolkit_widget)

    def size_hint(self):
        """ Return a size hint for the widget.

        """
        along_hint = 0
        ortho_hint = 0
        shell = self.shell_obj
        i = ['horizontal', 'vertical'].index(shell.orientation)
        j = 1 - i
        for child in shell.children:
            if child.visible:
                size_hint = child.size_hint()
                if size_hint == (-1, -1):
                    min_size = child.toolkit_widget.minimumSize()
                    size_hint = (min_size.width(), min_size.height())
                # FIXME: Add handle widths? QSplitter doesn't.
                along_hint += size_hint[i]
                ortho_hint = max(ortho_hint, size_hint[j])
        if shell.orientation == 'horizontal':
            return (along_hint, ortho_hint)
        else:
            return (ortho_hint, along_hint)

    def set_initial_sizes(self):
        """ Set the initial sizes for the children.

        """
        shell = self.shell_obj
        i = ['horizontal', 'vertical'].index(shell.orientation)
        sizes = []
        for child in shell.children:
            hint = child.size_hint()[i]
            if hint <= 0:
                min_size = child.toolkit_widget.minimumSize()
                hint = (min_size.width(), min_size.height())[i]
            sizes.append(hint)
        self.widget.setSizes(sizes)

