#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt
from .qt.QtGui import QMenu
from .qt_action import QtAction
from .qt_action_group import QtActionGroup
from .qt_widget import QtWidget


class QCustomMenu(QMenu):
    """ A custom subclass of QMenu which adds some convenience apis.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a QCustomMenu.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a QMenu.

        """
        super(QCustomMenu, self).__init__(*args, **kwargs)
        self._is_context_menu = False

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _onShowContextMenu(self, pos):
        """ A private signal handler for displaying the context menu.

        This handler is connected to the context menu requested signal
        on the parent widget when this menu is marked as a context
        menu.

        """
        parent = self.parentWidget()
        if parent is not None:
            global_pos = parent.mapToGlobal(pos)
            self.exec_(global_pos)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def isContextMenu(self):
        """ Whether this menu acts as a context menu for its parent.

        Returns
        -------
        result : bool
            True if this menu acts as a context menu, False otherwise.

        """
        return self._is_context_menu

    def setContextMenu(self, context):
        """ Set whether this menu acts as a context menu for its parent.

        Parameters
        ----------
        context : bool
            True if this menu should act as a context menu, False
            otherwise.

        """
        old_context = self._is_context_menu
        self._is_context_menu = context
        if old_context != context:
            parent = self.parentWidget()
            if parent is not None:
                handler = self._onShowContextMenu
                if context:
                    parent.setContextMenuPolicy(Qt.CustomContextMenu)
                    parent.customContextMenuRequested.connect(handler)
                else:
                    parent.setContextMenuPolicy(Qt.DefaultContextMenu)
                    parent.customContextMenuRequested.disconnect(handler)

    def removeActions(self, actions):
        """ Remove the given actions from the menu.

        Parameters
        ----------
        actions : iterable
            An iterable of QActions to remove from the menu.

        """
        remove = self.removeAction
        for action in actions:
            remove(action)


class QtMenu(QtWidget):
    """ A Qt implementation of an Enaml Menu.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying menu widget.

        """
        return QCustomMenu(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtMenu, self).create(tree)
        self.set_title(tree['title'])
        self.set_context_menu(tree['context_menu'])

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
    def child_removed(self, child):
        """  Handle the child removed event for a QtMenu.

        """
        if isinstance(child, QtMenu):
            self.widget().removeAction(child.widget().menuAction())
        elif isinstance(child, QtAction):
            self.widget().removeAction(child.widget())
        elif isinstance(child, QtActionGroup):
            self.widget().removeActions(child.actions())

    def child_added(self, child):
        """ Handle the child added event for a QtMenu.

        """
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

    def on_action_set_context_menu(self, content):
        """ Handle the 'set_context_menu' action from the Enaml widget.

        """
        self.set_context_menu(content['context_menu'])

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

    def set_context_menu(self, context):
        """ Set whether or not the menu is a context menu.

        """
        self.widget().setContextMenu(context)

