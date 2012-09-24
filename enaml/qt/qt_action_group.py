#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QActionGroup
from .qt_object import QtObject


class QCustomActionGroup(QActionGroup):
    """ A QActionGroup subclass which fixes some toggling issues.

    When a QActionGroup is set from non-exlusive to exclusive, it
    doesn't uncheck the non-current actions. It also does not keep
    track of the most recently checked widget when in non-exclusive
    mode, so that state is lost. This subclass corrects these issues.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a QCustomActionGroup.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a QActionGroup.

        """
        super(QCustomActionGroup, self).__init__(*args, **kwargs)
        self.triggered.connect(self.onTriggered)
        self._last_checked = None

    def onTriggered(self, action):
        """ The signal handler for the 'triggered' signal.

        """
        if action.isCheckable() and action.isChecked():
            if self.isExclusive():
                last = self._last_checked
                if last is not None and last is not action:
                    last.setChecked(False)
            self._last_checked = action

    def setExclusive(self, exclusive):
        """ Set the exclusive state of the action group.

        Parameters
        ----------
        exclusive : bool
            Whether or not the action group is exclusive.

        """
        super(QCustomActionGroup, self).setExclusive(exclusive)
        if exclusive:
            last = self._last_checked
            if last is not None:
                last.setChecked(True)
                for action in self.actions():
                    if action is not last:
                        action.setChecked(False)


class QtActionGroup(QtObject):
    """ A Qt implementation of an Enaml ActionGroup.

    """
    #: Store for the action ids
    _action_ids = []

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying action group widget.

        """
        return QCustomActionGroup(parent)

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(QtActionGroup, self).create(tree)
        self.set_action_ids(tree['action_ids'])
        self.set_exclusive(tree['exclusive'])
        self.set_enabled(tree['enabled'])
        self.set_visible(tree['visible'])

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtActionGroup, self).init_layout()
        widget = self.widget()
        find_child = self.find_child
        for action_id in self._action_ids:
            child = find_child(action_id)
            if child is not None:
                widget.addAction(child.widget())

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_exclusive(self, content):
        """ Handle the 'set_exclusive' action from the Enaml widget.

        """
        self.set_exclusive(content['exclusive'])

    def on_action_set_enabled(self, content):
        """ Handle the 'set_enabled' action from the Enaml widget.

        """
        self.set_enabled(content['enabled'])

    def on_action_set_visible(self, content):
        """ Handle the 'set_visible' action from the Enaml widget.

        """
        self.set_visible(content['visible'])
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_action_ids(self, action_ids):
        """ Set the action ids for the underlying control.

        """
        self._action_ids = action_ids

    def set_exclusive(self, exclusive):
        """ Set the exclusive state of the underlying control.

        """
        self.widget().setExclusive(exclusive)

    def set_enabled(self, enabled):
        """ Set the enabled state of the underlying control.

        """
        self.widget().setEnabled(enabled)

    def set_visible(self, visible):
        """ Set the visible state of the underlying control.

        """
        self.widget().setVisible(visible)

