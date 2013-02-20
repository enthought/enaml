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

    #: The mask to use for text input. The mask supports the following
    #: grammar:
    #: A   ASCII alphabetic character required. A-Z, a-z.
    #: a   ASCII alphabetic character permitted but not required.
    #: N   ASCII alphanumeric character required. A-Z, a-z, 0-9.
    #: n   ASCII alphanumeric character permitted but not required.
    #: X   Any character required.
    #: x   Any character permitted but not required.
    #: 9   ASCII digit required. 0-9.
    #: 0   ASCII digit permitted but not required.
    #: D   ASCII digit required. 1-9.
    #: d   ASCII digit permitted but not required (1-9).
    #: #   ASCII digit or plus/minus sign permitted but not required.
    #: H   Hexadecimal character required. A-F, a-f, 0-9.
    #: h   Hexadecimal character permitted but not required.
    #: B   Binary character required. 0-1.
    #: b   Binary character permitted but not required.
    #: >   All following alphabetic characters are uppercased.
    #: <   All following alphabetic characters are lowercased.
    #: !   Switch off case conversion.
    #: \   Use \ to escape the special characters listed above to use them as separators.
    #: 
    #: The mask consists of a string of mask characters and separators, optionally
    #: followed by a semicolon and the character used for blanks
    # Eg: 9 digit phone number: (999) 999-9999;_ 
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
        snap['mask'] = self.mask
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
            'text', 'mask', 'placeholder', 'echo_mode', 'max_length', 'read_only',
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

