#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from atom.api import Bool, observe

from enaml.core.declarative import Declarative, d_properties
from enaml.core.messenger import Messenger

from .action import Action


@d_properties('exclusive', 'enabled', 'visible')
class ActionGroup(Messenger, Declarative):
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

    @property
    def actions(self):
        """ A read only property which returns the group's actions.

        """
        isinst = isinstance
        items = (child for child in self.children if isinst(child, Action))
        return tuple(items)

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the ActionGroup.

        """
        snap = super(ActionGroup, self).snapshot()
        snap['exclusive'] = self.exclusive
        snap['enabled'] = self.enabled
        snap['visible'] = self.visible
        return snap

    @observe(r'^(exclusive|enabled|visible)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends the state change for the group.

        """
        # The superclass implementation is sufficient.
        super(ActionGroup, self).send_member_change(change)

