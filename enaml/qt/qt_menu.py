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
                widget.addActions(child.widget().actions())

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtMenu.

        This handler ensures that the child is inserted in the proper
        place in the menu.

        """
        child.initialize()
        index = self.index_of(child)
        if index != -1:
            before = None
            children = self.children()
            if index < len(children) - 1:
                temp = children[index + 1]
                if isinstance(temp, QtMenu):
                    before = temp.widget().menuAction()
                elif isinstance(temp, QtAction):
                    before = temp.widget()
                elif isinstance(temp, QtActionGroup):
                    actions = temp.widget().actions()
                    if actions:
                        before = actions[0]
            widget = self.widget()
            if isinstance(child, QtMenu):
                widget.insertMenu(before, child.widget())
            elif isinstance(child, QtAction):
                widget.insertAction(before, child.widget())
            elif isinstance(child, QtActionGroup):
                widget.insertActions(before, child.widget().actions())

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

