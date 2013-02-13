#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Unicode, Enum, List

from enaml.validation.validator import Validator

from .control import Control


class MultiLineField(Control):
    """ A multi line editable text widget.

    """
    #: The unicode text to display in the field.
    text = Unicode

    #: The list of actions which should cause the client to submit its
    #: text to the server for validation and update. The currently
    #: supported values are 'lost_focus' and 'return_pressed'.
    submit_triggers = List(
        Enum('lost_focus', 'text_changed'), ['lost_focus', 'text_changed']
    )

    #: Whether or not the field is read only. Defaults to False.
    read_only = Bool(False)

    #: How strongly a component hugs it's contents' width. Text boxes ignore
    #: both the width and height hugs by default, so they expand freely in both
    #: directions
    hug_width = 'ignore'
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the textedit

        """
        snap = super(MultiLineField, self).snapshot()
        snap['text'] = self.text
        snap['submit_triggers'] = self.submit_triggers
        snap['read_only'] = self.read_only
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(MultiLineField, self).bind()
        attrs = (
            'text', 'read_only',
        )
        self.publish_attributes(*attrs)
        self.on_trait_change(self._send_submit_triggers, 'submit_triggers[]')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _send_submit_triggers(self):
        """ Send the new submit triggers to the client widget.

        """
        content = {'submit_triggers': self.submit_triggers}
        self.send_action('set_submit_triggers', content)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_submit_text(self, content):
        """ Handle the 'submit_text' action from the client widget.

        """
        text = content['text']
        self.set_guarded(text=text)
