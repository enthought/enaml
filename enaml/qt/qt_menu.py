#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QMenu, QAction, QActionGroup
from .qt_widget_component import QtWidgetComponent


class QtMenu(QtWidgetComponent):
    """ A Qt implementation of an Enaml Menu.

    """
    #: Storage for the menu item ids
    _item_ids = []

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
        self.set_item_ids(tree['item_ids'])
        self.set_title(tree['title'])

    def init_layout(self):
        """ Initialize the layout for the underlying widget.

        """
        super(QtMenu, self).init_layout()
        widget = self.widget()
        find_child = self.find_child
        for item_id in self._item_ids:
            child = find_child(item_id)
            if child is not None:
                child_widget = child.widget()
                if isinstance(child_widget, QMenu):
                    widget.addMenu(child_widget)
                elif isinstance(child_widget, QAction):
                    widget.addAction(child_widget)
                elif isinstance(child_widget, QActionGroup):
                    widget.addActions(child_widget.actions())

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
                temp = children[index + 1].widget()
                if isinstance(temp, QMenu):
                    before = temp.menuAction()
                elif isinstance(temp, QAction):
                    before = temp
                elif isinstance(temp, QActionGroup):
                    actions = temp.actions()
                    if actions:
                        before = actions[0]
            widget = self.widget()
            child_widget = child.widget()
            if isinstance(child_widget, QMenu):
                widget.insertMenu(before, child_widget)
            elif isinstance(child_widget, QAction):
                widget.insertAction(before, child_widget)
            elif isinstance(child_widget, QActionGroup):
                widget.insertActions(before, child_widget.actions())

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
    def set_item_ids(self, item_ids):
        """ Set the item ids of the underlying widget..

        """
        self._item_ids = item_ids

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

