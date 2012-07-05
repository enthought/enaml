#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Int, Unicode, Enum, List, Str

from .constraints_widget import ConstraintsWidget


class Field(ConstraintsWidget):
    """ A single-line editable text widget.

    """
    #: The unicode text to display in the field.
    text = Unicode

    #: A regular expression string which is checked every time the user
    #: presses a key. If the new text does not pass this expressions, 
    #: then the user will not be able to add that character. The default
    #: expression accepts all input.
    key_validator = Unicode(ur'.*')

    #: A regular expression which is checked when the user attempt to
    #: submits the value in the field. If the text does not pass this
    #: expression, it will not be submitted and the background color
    #: of the field will be changed to the 'error_color'. The default
    #: expression accepts all input.
    submit_validator = Unicode(ur'.*')

    #: The background color to use if the user attempts to submit text
    #: which does not pass the submit validator. Supports CSS style
    #: color strings.
    error_color = Str

    #: The maximum length of the field in characters. The default value
    #: is Zero and indicates there is no maximum length.
    max_length = Int(0)

    #: Whether or not the field is read only. Defaults to False.
    read_only = Bool(False)

    #: The grayed-out text to display if the field is empty and the
    #: widget doesn't have focus. Defaults to the empty string.
    placeholder_text = Unicode
    
    #: How to obscure password text in the field.
    password_mode = Enum('normal', 'password', 'silent')

    #: A list of strings which indicates when the text the in the field
    #: should be converted to a Python object representation and stored 
    #: in the 'value' attribute. The default mode triggers submissions 
    #: on lost focus events and return pressed events. Allowable modes 
    #: are 'lost_focus', and 'return_pressed'. The default value is to 
    #: submit on either lost focus or return pressed. A submission can
    #: also be performed manually by calling the 'submit()' method.
    submit_mode = List(
        Enum('lost_focus', 'return_pressed'), 
        value=['lost_focus', 'return_pressed'],
    )
   
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
            'key_validator': self.key_validator,
            'submit_validator': self.submit_validator,
            'error_color': self.error_color,
            'max_length': self.max_length,
            'read_only': self.read_only,
            'placeholder_text' : self.placeholder_text,
            'password_mode' : self.password_mode,
            'submit_mode' : self.submit_mode,
        }
        super_attrs.update(attrs)
        return super_attrs

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Field, self).bind()
        attrs = (
            'text', 'key_validator', 'submit_validator', 'error_color',
            'max_length', 'read_only', 'placeholder_text', 'password_mode', 
            'submit_mode',
        )
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_message_event_changed(self, payload):
        """ Handle the 'event-changed' action from the client widget.

        """
        text = payload['text']
        self.set_guarded(text=text)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def submit(self):
        """ A method which will perform a manual submission of the text
        in the field. This is useful for form-based submission where all
        the values for several fields should all be submitted at once.

        """
        self.send_message({'action': 'submit'})

