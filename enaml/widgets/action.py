#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, Bool, Str

from enaml.core.messenger import Messenger
from enaml.core.trait_types import EnamlEvent


class Action(Messenger):
    """ A non visible widget used in a ToolBar or Menu.

    An Action represents an actionable item in a ToolBar or a Menu.
    Though an Action itself is a non-visible component, it will be
    rendered in an appropriate fashion for the location where it is
    used.

    """
    #: The text label associate with the action.
    text = Unicode

    #: The tool tip text to use for this action. Typically displayed
    #: as a small label when the user hovers over the action.
    tool_tip = Unicode

    #: The text that is displayed in the status bar when the user
    #: hovers over the action.
    status_tip = Unicode

    #: The source url for the icon to use for the Action.
    icon_source = Str

    #: Whether or not the action can be checked.
    checkable = Bool(False)

    #: Whether or not the action is checked. This value only has meaning
    #: if 'checkable' is set to True.
    checked = Bool(False)

    #: Whether or not the item representing the action is enabled.
    enabled = Bool(True)

    #: Whether or not the item representing the action is visible.
    visible = Bool(True)

    #: Whether or not the action should be treated as a separator. If
    #: this value is True, none of the other values have meaning.
    separator = Bool(False)

    #: An event fired when the action is triggered by user interaction.
    #: They payload will be the current checked state.
    triggered = EnamlEvent

    #: An event fired when a checkable action changes its checked state.
    #: The payload will be the current checked state.
    toggled = EnamlEvent

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the Action.

        """
        snap = super(Action, self).snapshot()
        snap['text'] = self.text
        snap['tool_tip'] = self.tool_tip
        snap['status_tip'] = self.status_tip
        snap['icon_source'] = self.icon_source
        snap['checkable'] = self.checkable
        snap['checked'] = self.checked
        snap['enabled'] = self.enabled
        snap['visible'] = self.visible
        snap['separator'] = self.separator
        return snap

    def bind(self):
        """ Binds the change handlers for the Action.

        """
        super(Action, self).bind()
        attrs = (
            'text', 'tool_tip', 'status_tip', 'icon_source', 'checkable',
            'checked', 'enabled', 'visible', 'separator'
        )
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_triggered(self, content):
        """ Handle the 'triggered' action from the client widget.

        """
        checked = content['checked']
        self.set_guarded(checked=checked)
        self.triggered(checked)

    def on_action_toggled(self, content):
        """ Handle the 'toggled' action from the client widget.

        """
        checked = content['checked']
        self.set_guarded(checked=checked)
        self.toggled(checked)

