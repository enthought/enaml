#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (
    HasTraits, Bool, Int, Unicode, Enum, List, Dict, Instance, ReadOnly
)

from enaml.core.trait_types import EnamlEvent
from enaml.validation import Validator

from .constraints_widget import ConstraintsWidget


class TextEditEvent(HasTraits):
    """ An event object that is emitted when the client edits text.

    """
    #: The original unicode text in the field pre-edit.
    orig_text = ReadOnly

    #: The unicode text that was edited in the client control. This
    #: text can be modified to change what is applied to the field.
    edit_text = Unicode

    #: Whether or not the edit text is considered valid. This can
    #: be modified to change whether or not the edit text is valid.
    edit_valid = Bool


class Field(ConstraintsWidget):
    """ A single-line editable text widget.

    """
    #: The unicode text to display in the field.
    text = Unicode

    #: An event fired when text has been edited by the client. The 
    #: payload will be an instance of TextEditEvent and can be used
    #: to control the subsequent update to the 'text' attribute.
    text_edited = EnamlEvent

    #: The mask to use for text input. 
    #: TODO - describe and implement this mask
    mask = Unicode

    #: The validator to use with the field. Note that the validator will
    #: executed client-side.
    validator = Instance(Validator)

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
        snap['validator'] = self._snap_validator()
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
        self.on_trait_change(self._send_validator, 'validator')
        self.on_trait_change(self._send_edit_triggers, 'edit_triggers[]')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _snap_validator(self):
        """ A private method which returns the serializable form of the
        current validator.

        """
        validator = self.validator
        return validator.as_dict() if validator is not None else None

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_text_edited(self, content):
        """ Handle the 'text_edited' action from the client widget.

        """
        orig_text = self.text
        edit_text = content['text']
        edit_valid = content['valid']
        
        validator = self.validator
        if validator is not None:
            edit_text, edit_valid = validator.validate(
                orig_text, edit_text, edit_valid
            )
        
        event = TextEditEvent(
            orig_text=orig_text, edit_text=edit_text, edit_valid=edit_valid,
        )
        self.text_edited(event)
        
        if event.edit_valid:
            # If the edit is valid and text differs from the original
            # edit text, we push an update to the client.
            if edit_text != event.edit_text:
                content = {'text': event.edit_text}
                self.send_action('set_text', content)
            self.set_guarded(text=event.edit_text)

    def _send_validator(self):
        """ Send the new validator to the client widget.

        """
        content = {'validator': self._snap_validator()}
        self.send_action('set_validator', content)

    def _send_edit_triggers(self):
        """ Send the new edit triggers to the client widget.

        """
        content = {'edit_triggers': self.edit_triggers}
        self.send_action('set_edit_triggers', content)

