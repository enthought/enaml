#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Int, Unicode, Enum, List, Dict

from .constraints_widget import ConstraintsWidget


#: The default validators to use in a Field.
DEFAULT_FIELD_VALIDATORS = [
    {'type': 'null',
     'triggers': ['return-pressed', 'lost-focus']},
]


class Field(ConstraintsWidget):
    """ A single-line editable text widget.

    """
    #: The unicode text to display in the field.
    text = Unicode

    #: A list of dictionaries representing the validation to perform 
    #: on the field. Validators will be executed in order and will 
    #: stop at the first failing validator. The client will only
    #: send a text update if all validators pass. The validator format 
    #: is specified in the file validator_format.js. The default 
    #: validator accepts all input and triggers on 'lost-focus' and 
    #: 'return-pressed'.
    validators = List(Dict, value=DEFAULT_FIELD_VALIDATORS)

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
    def creation_attributes(self):
        """ Returns the dict of creation attributes for the control.

        """
        super_attrs = super(Field, self).creation_attributes()
        attrs = {
            'text': self.text,
            'validators': self.validators,
            'placeholder' : self.placeholder,
            'echo_mode' : self.echo_mode,
            'max_length': self.max_length,
            'read_only': self.read_only,
        }
        super_attrs.update(attrs)
        return super_attrs

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

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_message_event_changed(self, payload):
        """ Handle the 'event-changed' action from the client widget.

        """
        text = payload['text']
        self.set_guarded(text=text)

    def _send_validators(self):
        """ Send the new validators to the client widget.

        """
        payload = {'action': 'set-validators', 'validators': self.validators}
        self.send_message(payload)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def validate(self):
        """ A method which will perform a manual validation of the text
        in the field.

        """
        self.send_message({'action': 'validate'})

