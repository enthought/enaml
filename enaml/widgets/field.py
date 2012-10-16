#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Int, Unicode, Enum, List, Instance

from enaml.validation.validator import Validator

from .control import Control


class Field(Control):
    """ A single line editable text widget.

    """
    #: The unicode text to display in the field.
    text = Unicode

    #: The mask to use for text input.
    #: TODO - describe and implement this mask
    mask = Unicode

    #: The validator to use for this field. If the validator provides
    #: a client side validator, then text will only be submitted if it
    #: passes that validator.
    validator = Instance(Validator)

    #: The list of actions which should cause the client to submit its
    #: text to the server for validation and update. The currently
    #: supported values are 'lost_focus' and 'return_pressed'.
    submit_triggers = List(
        Enum('lost_focus', 'return_pressed'), ['lost_focus', 'return_pressed']
    )

    #: The grayed-out text to display if the field is empty and the
    #: widget doesn't have focus. Defaults to the empty string.
    placeholder = Unicode

    #: How to display the text in the field. Valid values are 'normal'
    #: which displays the text as normal, 'password' which displays the
    #: text with an obscured character, and 'silent' which displays no
    #: text at all but still allows input.
    echo_mode = Enum('normal', 'password', 'silent')

    #: The maximum length of the field in characters. The default value
    #: is Zero and indicates there is no maximum length.
    max_length = Int(0)

    #: Whether or not the field is read only. Defaults to False.
    read_only = Bool(False)

    #: How strongly a component hugs it's contents' width. Fields ignore
    #: the width hug by default, so they expand freely in width.
    hug_width = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the field.

        """
        snap = super(Field, self).snapshot()
        snap['text'] = self.text
        snap['validator'] = self._client_validator()
        snap['submit_triggers'] = self.submit_triggers
        snap['placeholder'] = self.placeholder
        snap['echo_mode'] = self.echo_mode
        snap['max_length'] = self.max_length
        snap['read_only'] = self.read_only
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Field, self).bind()
        attrs = (
            'text', 'placeholder', 'echo_mode', 'max_length', 'read_only',
        )
        self.publish_attributes(*attrs)
        self.on_trait_change(self._send_validator, 'validator')
        self.on_trait_change(self._send_submit_triggers, 'submit_triggers[]')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _client_validator(self):
        """ A private method which returns the current client validator.

        """
        v = self.validator
        return v.client_validator() if v is not None else None

    def _send_validator(self):
        """ Send the new validator to the client widget.

        """
        content = {'validator': self._client_validator()}
        self.send_action('set_validator', content)

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
        edit_text = content['text']
        validator = self.validator
        if validator is not None:
            text, valid = validator.validate(edit_text, self)
        else:
            text, valid = edit_text, True
        if valid:
            # If the new text differs from the original edit text,
            # we push an update to the client.
            if text != edit_text:
                content = {'text': text}
                self.send_action('set_text', content)
            self.set_guarded(text=text)
        else:
            # notify the client that server validation failed.
            content = {'text': text}
            self.send_action('invalid_text', content)

