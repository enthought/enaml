#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

from .qt_object import QtObject
from .qt_widget import QtWidget

class QtTransientStatusWidgets(QtObject):
    """ A Qt implementation of the transient children of an Enaml StatusBar

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtTransientStatusWidgets, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, QtWidget):
                widget.addMenu(child.widget())

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtWidgetBar.

        """
        if isinstance(child, QtWidget):
            self.widget().removeAction(child.widget().menuAction())

    def child_added(self, child):
        """ Handle the child added event for a QtWidgetBar.

        """
        if isinstance(child, QtWidget):
            before = self.find_next_action(child)
            self.widget().insertMenu(before, child.widget())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def find_next_action(self, child):
        """ Get the QAction instance which comes immediately after the
        actions of the given child.

        Parameters
        ----------
        child : QtWidget
            The child menu of interest.

        Returns
        -------
        result : QAction or None
            The QAction which comes immediately after the actions of the
            given child, or None if no actions follow the child.

        """
        # The target action must be tested for membership against the
        # current actions on the menu bar itself, since this method may
        # be called after a child is added, but before the actions for
        # the child have actually added to the menu.
        index = self.index_of(child)
        if index != -1:
            actions = set(self.widget().actions())
            for child in self.children()[index + 1:]:
                if isinstance(child, QtWidget):
                    target = child.widget().menuAction()
                    if target in actions:
                        return target

