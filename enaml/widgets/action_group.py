#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Property, cached_property

from .action import Action
from .messenger_widget import MessengerWidget


class ActionGroup(MessengerWidget):
    """ A non visible widget used to group actions.

    An action group can be used in a MenuBar or a ToolBar to group a 
    related set of Actions and apply common operations to the set. The
    primary use of an action group is to make any checkable actions in
    the group mutually exclusive.

    """
    #: Whether or not the actions in this group are exclusive.
    exclusive = Bool(True)

    #: Whether or not the actions in this group are enabled.
    enabled = Bool(True)

    #: Whether or not the actions in this group are visible.
    visible = Bool(True)

    #: A read only property which returns the actions for this group.
    actions = Property(depends_on='children[]')

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the ActionGroup.

        """
        snap = super(ActionGroup, self).snapshot()
        snap['action_ids'] = self._snap_action_ids()
        snap['exclusive'] = self.exclusive
        snap['enabled'] = self.enabled
        snap['visible'] = self.visible
        return snap

    def bind(self):
        """ Binds the change handlers for the ActionGroup.

        """
        super(ActionGroup, self).bind()
        self.publish_attributes('exclusive', 'enabled', 'visible')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_actions(self):
        """ The getter for the 'actions' property.

        Returns
        -------
        result : tuple
            The tuple of Actions defined as children of this ActionGroup.

        """
        isinst = isinstance
        items = (child for child in self.children if isinst(child, Action))
        return tuple(items)

    def _snap_action_ids(self):
        """ Returns the list of widget ids for the group's actions.

        """
        return [action.widget_id for action in self.actions]
