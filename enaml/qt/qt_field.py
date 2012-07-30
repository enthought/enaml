#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import re

from .qt.QtGui import QLineEdit, QWhatsThis
from .qt.QtCore import Signal, QTimer
from .qt_constraints_widget import QtConstraintsWidget


ECHO_MODES = {
    'normal': QLineEdit.Normal,
    'password' : QLineEdit.Password,
    'silent' : QLineEdit.NoEcho
}


# XXX these will likely be common to all Python clients
def null_validator(text):
    """ A validator which validates all input as acceptable.

    """
    return text


def regex_validator(regex):
    """ Creates a callable which will validate text input against the
    provided regex string.

    Parameters
    ----------
    regex : string
        A regular expression string to use for matching.

    Returns
    -------
    results : callable
        A callable which returns the original text if it matches the
        regex, or raises a ValueError if it doesn't.

    """
    regex = re.compile(regex, re.UNICODE)
    def validator(text):
        if regex.match(text):
            return text
        raise ValueError
    return validator


validator_factories = {
    'null': lambda: null_validator,
    'regex_validator': regex_validator,
}


def parse_validators(validators):
    """ Parses a list of validator dicts into a list of tuples.
    This is used internally by the QtField to dispatch its
    validation behaviors.
    
    """
    res = []
    for info in validators:
        vtype = info['type']
        factory = validator_factories.get(vtype, None)
        if factory is not None:
            vldr = factory(**info['arguments'])
            item = (info, vldr)
            res.append(item)
    return res


class QtFocusLineEdit(QLineEdit):
    """ A QLineEdit subclass which converts a lost focus event into 
    a lost focus signal.

    """
    lostFocus = Signal()

    def focusOutEvent(self, event):
        self.lostFocus.emit()
        return super(QtFocusLineEdit, self).focusOutEvent(event)


class QtField(QtConstraintsWidget):
    """ A Qt4 implementation of an Enaml Field.

    """
    def create(self):
        """ Create underlying QLineEdit widget.

        """
        self.widget = QtFocusLineEdit(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the attributes of the widget

        """
        super(QtField, self).initialize(attrs)
        self.set_text(attrs['text'])
        self.set_placeholder(attrs['placeholder'])
        self.set_echo_mode(attrs['echo_mode'])
        self.set_max_length(attrs['max_length'])
        self.set_read_only(attrs['read_only'])
        self.validators = parse_validators(attrs['validators'])
        self.triggers = attrs['triggers']
        self.dirty = False
        self.valid = True # hook for stylesheets (XXX validate on initialization?)
        self.widget.lostFocus.connect(self.on_lost_focus)
        self.widget.returnPressed.connect(self.on_return_pressed)
        self.widget.textEdited.connect(self.on_text_edited)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_lost_focus(self):
        """ Event handler for lost_focus

        """
        if self.dirty and 'lost-focus' in self.triggers:
            validators = self.validators
            if validators:
                self._run_validators(validators)

    def on_return_pressed(self):
        """ Event handler for return_pressed

        """
        if self.dirty and 'return-pressed' in self.triggers:
            validators = self.validators
            if validators:
                self._run_validators(validators)

    def on_text_edited(self):
        """ Mark the widget as dirty so that validation can take place.

        """
        self.dirty = True

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_text(self, payload):
        """ Handle the 'set-text' action from the Enaml widget.

        """
        self.set_text(payload['text'])

    def on_message_set_validators(self, payload):
        """ Handle the 'set-validators' action from the Enaml widget.

        """
        self.validators = parse_validators(payload['validators'])

    def on_message_set_triggers(self, payload):
        """ Handle the 'set-validators' action from the Enaml widget.

        """
        self.triggers = payload['triggers']

    def on_message_set_placeholder(self, payload):
        """ Hanlde the 'set-placeholder' action from the Enaml widget.

        """
        self.set_placeholder(payload['placeholder'])

    def on_message_set_echo_mode(self, payload):
        """ Handle the 'set-echo_mode' action from the Enaml widget.

        """
        self.set_echo_mode(payload['echo_mode'])

    def on_message_set_max_length(self, payload):
        """ Handle the 'set-max_length' action from the Enaml widget.

        """
        self.set_max_length(payload['max_length'])

    def on_message_set_read_only(self, payload):
        """ Handle the 'set-read_only' action from the Enaml widget.

        """
        self.set_read_only(payload['read_only'])

    def on_message_validate(self, payload):
        """ Handle the 'validate' action from the Enaml widget.

        """
        if self.dirty:
            validators = self.validators
            if validators:
                self._run_validators(validators)
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the text in the underlying widget.

        """
        self.widget.setText(text)

    def set_placeholder(self, text):
        """ Set the placeholder text of the underlying widget.

        """
        self.widget.setPlaceholderText(text)
        
    def set_echo_mode(self, mode):
        """ Set the echo mode of the underlying widget.

        """
        self.widget.setEchoMode(ECHO_MODES[mode])

    def set_max_length(self, length):
        """ Set the maximum text length in the underlying widget.

        """
        if length <= 0 or length > 32767:
            length = 32767
        self.widget.setMaxLength(length)

    def set_read_only(self, read_only):
        """ Set whether or not the widget is read only.

        """
        self.widget.setReadOnly(read_only)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _run_validators(self, validators):
        """ Run the validation process for the given trigger.

        """
        text = orig = self.widget.text()
        for info, validator in validators:
            try:
                text = validator(text)
            except ValueError:
                self.valid = False
                self._validation_failure(orig, text, info)
                return

        # Everything validated, we need to send the text update to
        # the Enaml widget and update the control if the validators 
        # have changed the text.
        if orig != text:
            pos = self.widget.cursorPosition()
            self.widget.setText(text)
            self.widget.setCursorPosition(pos)

        payload = {'action': 'event-changed', 'text': text}
        self.send_message(payload)
        
        self.valid = True
        self.dirty = False

    def _validation_failure(self, orig, text, info):
        """ Handle a validator failing its validation.

        """
        # This is just a temporary popup hack for now until we get 
        # Naveen's pretty popup widget in place.
        msg = info.get('message', '')
        msg = 'Validation Failure: %s' % msg
        widget = self.widget
        globalPos = widget.mapToGlobal(widget.pos())
        QWhatsThis.showText(globalPos, msg, widget)
        QTimer.singleShot(2000, QWhatsThis.hideText)

