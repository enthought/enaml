#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QMenu
from .qt_action import QtAction
from .qt_action_group import QtActionGroup
from .qt_widget_component import QtWidgetComponent


class QtMenu(QtWidgetComponent):
    """ A Qt implementation of an Enaml Menu.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying menu widget.

        """
        return QMenu(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtMenu, self).create(tree)
        self.set_title(tree['title'])

    def init_layout(self):
        """ Initialize the layout for the underlying widget.

        """
        super(QtMenu, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, QtMenu):
                widget.addMenu(child.widget())
            elif isinstance(child, QtAction):
                widget.addAction(child.widget())
            elif isinstance(child, QtActionGroup):
                widget.addActions(child.actions())

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtMenu.

        This handler ensures that the child is inserted in the proper
        place in the menu.

        """
        child.initialize()
        before = self.find_next_action(child)
        if isinstance(child, QtMenu):
            self.widget().insertMenu(before, child.widget())
        elif isinstance(child, QtAction):
            self.widget().insertAction(before, child.widget())
        elif isinstance(child, QtActionGroup):
            self.widget().insertActions(before, child.actions())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def find_next_action(self, child):
        """ Get the QAction instance which comes immediately after the
        actions of the given child.

        Parameters
        ----------
        child : QtMenu, QtActionGroup, or QtAction
            The child of interest.

        Returns
        -------
        result : QAction or None
            The QAction which comes immediately after the actions of the
            given child, or None if no actions follow the child.

        """
        # The target action must be tested for membership against the 
        # current actions on the menu itself, since this method may be
        # called after a child is added, but before the actions for the
        # child have actually been added to the menu.
        index = self.index_of(child)
        if index != -1:
            actions = set(self.widget().actions())
            for child in self.children()[index + 1:]:
                target = None
                if isinstance(child, QtMenu):
                    target = child.widget().menuAction()
                elif isinstance(child, QtAction):
                    target = child.widget()
                elif isinstance(child, QtActionGroup):
                    acts = child.actions()
                    target = acts[0] if acts else None
                if target in actions:
                    return target

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_title(self, content):
        """ Handle the 'set_title' action from the Enaml widget.

        """
        self.set_title(content['title'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_visible(self, visible):
        """ Set the visibility on the underlying widget.

        This is an overridden method which sets the visibility on the
        underlying QAction for the menu instead of on the menu itself.

        """ 
        self.widget().menuAction().setVisible(visible)

    def set_title(self, title):
        """ Set the title of the underlying widget.

        """
        self.widget().setTitle(title)

