#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (
    HasTraits, Bool, Int, Unicode, Enum, List, Dict, Instance, ReadOnly
)

from enaml.core.trait_types import EnamlEvent
from enaml.validators import Validator

from .constraints_widget import ConstraintsWidget


class TextEditEvent(HasTraits):
    """ An event object that is emitted when the client edits text.

    """
    #: The unicode text that was edited in the client control.
    edit_text = ReadOnly

    #: Whether or not the edit text passed all client validators.
    edit_valid = ReadOnly

    #: The unicode text to apply to the 'text' attribute of the Field.
    #: This text will be the same as 'edit_text' until changed.
    text = Unicode
    def _text_default(self):
        return self.edit_text

    #: Whether or not the 'text' attribute should be considered valid.
    #: This will be the same as 'edit_valid' until changed. If this
    #: value is True at the end of event processing, then the 'text'
    #: attribute of the Field will be assigned the value of 'text'.
    valid = Bool
    def _valid_default(self):
        return self.edit_valid

    #: Whether or not the value of the client field should be restored
    #: to the value of the 'text' attribute on the Field if 'valid' is
    #: False at the end of event processing.
    restore = Bool(False)


class Field(ConstraintsWidget):
    """ A single-line editable text widget.

    """
    #: The unicode text to display in the field.
    text = Unicode

    #: An event fired when text has been edited by the client. The 
    #: payload will be an instance of TextEditEvent and can be used
    #: to control the subsequent update to the 'text' attribute.
    text_edited = EnamlEvent

    #: The mask to use for input text. 
    #: TODO - describe and implement this mask
    mask = Unicode

    #: A list of dictionaries representing the validation to perform on
    #: the field client-side. Validators will be executed in order and 
    #: will stop at the first failing validator. The validator format
    #: is specified in the file validator_format.js. If no validators
    #: are supplied, all input is accepted. Validators are executed by
    #: the client on every key press.
    validators = List(Dict)

    #: The actions which should cause the client to send a text edited
    #: event back to the server if the text in the control has changed.
    edit_triggers = List(
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
        """ Returns the dict of creation attributes for the control.

        """
        snap = super(Field, self).snapshot()
        snap['text'] = self.text
        snap['validators'] = self.validators
        snap['edit_triggers'] = self.edit_triggers
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
        self.on_trait_change(self._send_validators, 'validators[]')
        self.on_trait_change(self._send_edit_triggers, 'edit_triggers[]')

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_text_edited(self, content):
        """ Handle the 'text_edited' action from the client widget.

        """
        text = content['text']
        valid = content['valid']
        event = TextEditEvent(edit_text=text, edit_valid=valid)
        self.text_edited(event)
        if event.valid:
            if event.text != event.edit_text:
                self.text = event.text
            else:
                self.set_guarded(text=event.text)
        else:
            if event.restore:
                content = {'text': self.text}
                self.send_action('set_text', content)

    def _send_validators(self):
        """ Send the new validators to the client widget.

        """
        content = {'validators': self.validators}
        self.send_action('set_validators', content)

    def _send_edit_triggers(self):
        """ Send the new edit triggers to the client widget.

        """
        content = {'edit_triggers': self.edit_triggers}
        self.send_action('set_edit_triggers', content)

