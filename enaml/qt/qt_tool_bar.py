#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt
from .qt.QtGui import QToolBar, QAction, QActionGroup, QMainWindow
from .qt_constraints_widget import QtConstraintsWidget


#: A mapping from Enaml orientation to Qt Orientation
_ORIENTATION_MAP = {
    'horizontal': Qt.Horizontal,
    'vertical': Qt.Vertical,
}


class QtToolBar(QtConstraintsWidget):
    """ A Qt implementation of an Enaml ToolBar.

    """
    #: Storage for the tool bar item ids. 
    _item_ids = []

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying tool bar widget.

        """
        return QToolBar(parent)

    def create(self, tree):
        """ Create and initialize the underlying tool bar control.

        """
        super(QtToolBar, self).create(tree)
        self.set_item_ids(tree['item_ids'])
        self.set_orientation(tree['orientation'])
        self.set_movable(tree['movable'])
        self.set_floatable(tree['floatable'])
        self.set_floating(tree['floating'])
        self.set_dock_area(tree['dock_area'])
        self.set_allowed_dock_areas(tree['allowed_dock_areas'])

    def init_layout(self):
        """ Initialize the layout for the toolbar.

        """
        super(QtToolBar, self).init_layout()
        widget = self.widget()
        find_child = self.find_child
        for item_id in self._item_ids:
            child = find_child(item_id)
            if child is not None:
                child_widget = child.widget()
                if isinstance(child_widget, QAction):
                    widget.addAction(child_widget)
                elif isinstance(child_widget, QActionGroup):
                    widget.addActions(child_widget.actions())

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_movable(self, content):
        """ Handle the 'set_movable' action from the Enaml widget.

        """
        self.set_movable(content['movable'])

    def on_action_set_floatable(self, content):
        """ Handle the 'set_floatable' action from the Enaml widget.

        """
        self.set_floatable(content['floatable'])

    def on_action_set_floating(self, content):
        """ Handle the 'set_floating' action from the Enaml widget.

        """
        self.set_floating(content['floating'])

    def on_action_set_dock_area(self, content):
        """ Handle the 'set_dock_area' action from the Enaml widget.

        """
        self.set_dock_area(content['dock_area'])

    def on_action_set_allowed_dock_areas(self, content):
        """ Handle the 'set_allowed_dock_areas' action from the Enaml
        widget.

        """
        self.set_allowed_dock_areas(content['allowed_dock_areas'])

    def on_action_set_orientation(self, content):
        """ Handle the 'set_orientation' action from the Enaml widget.

        """
        self.set_orientation(content['orientation'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_item_ids(self, item_ids):
        """ Set the item ids for the underlying widget.

        """
        self._item_ids = item_ids

    def set_orientation(self, orientation):
        """ Set the orientation of the underlying widget.

        """
        # If the tool bar is a child of a QMainWindow, then that window
        # will take control of setting its orientation and changes to
        # the orientation by the user must be ignored.
        widget = self.widget()
        parent = widget.parent()
        if not isinstance(parent, QMainWindow):
            widget.setOrientation(_ORIENTATION_MAP[orientation])

    def set_movable(self, movable):
        """ Set the movable state on the underlying widget.

        """
        self.widget().setMovable(movable)

    def set_floatable(self, floatable):
        """ Set the floatable state on the underlying widget.

        """
        self.widget().setFloatable(floatable)

    def set_floating(self, floating):
        """ Set the floating staet on the underlying widget.

        """
        pass

    def set_dock_area(self, dock_area):
        """ Set the dock area on the underyling widget.

        """
        pass

    def set_allowed_dock_areas(self, dock_areas):
        """ Set the allowed dock areas on the underlying widget.

        """
        pass

