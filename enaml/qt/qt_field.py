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


def null_validator(text):
    """ A validator which validates all input as acceptable.

    """
    return text


def regexp_validator(regexp):
    """ Creates a callable which will validate text input against the
    provided regex string.

    Parameters
    ----------
    regexp : string
        A regular expression string to use for matching.

    Returns
    -------
    results : callable
        A callable which returns the original text if it matches the
        regex, or raises a ValueError if it doesn't.

    """
    regexp = re.compile(regexp, re.UNICODE)
    def validator(text):
        if regexp.match(text):
            return text
        raise ValueError
    return validator


def parse_validators(validators):
    """ Parses a list of validator dicts into a dict of tuples keyed
    on the trigger type. This is used internally by the QtField to
    dispatch its validation behaviors.
    
    """
    res = {'all': []}
    for info in validators:
        vtype = info['type']
        if vtype == 'null':
            vldr = null_validator
        elif vtype == 'regexp':
            vldr = regexp_validator(info['regexp'])
        else:
            vldr = None 
        if vldr is not None:
            item = (info, vldr)
            res['all'].append(item)
            triggers = info.get('triggers')
            if triggers:
                for trigger in triggers:
                    if trigger not in res:
                        res[trigger] = []
                    res[trigger].append(item)
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
        self.dirty = False
        self.widget.lostFocus.connect(self.on_lost_focus)
        self.widget.returnPressed.connect(self.on_return_pressed)
        self.widget.textEdited.connect(self.on_text_edited)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_lost_focus(self):
        """ Event handler for lost_focus

        """
        if self.dirty:
            validators = self.validators.get('lost-focus')
            if validators:
                self._run_validators(validators)

    def on_return_pressed(self):
        """ Event handler for return_pressed

        """
        if self.dirty:
            validators = self.validators.get('return-pressed')
            if validators:
                self._run_validators(validators)

    def on_text_edited(self):
        """ Mark the widget as dirty so that validation can take place.

        """
        self.dirty = True

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_text(self, content):
        """ Handle the 'set_text' action from the Enaml widget.

        """
        self.set_text(content['text'])

    def on_action_set_validators(self, content):
        """ Handle the 'set_validators' action from the Enaml widget.

        """
        self.validators = parse_validators(content['validators'])

    def on_action_set_placeholder(self, content):
        """ Hanlde the 'set_placeholder' action from the Enaml widget.

        """
        self.set_placeholder(content['placeholder'])

    def on_action_set_echo_mode(self, content):
        """ Handle the 'set_echo_mode' action from the Enaml widget.

        """
        self.set_echo_mode(content['echo_mode'])

    def on_action_set_max_length(self, content):
        """ Handle the 'set_max_length' action from the Enaml widget.

        """
        self.set_max_length(content['max_length'])

    def on_action_set_read_only(self, content):
        """ Handle the 'set_read_only' action from the Enaml widget.

        """
        self.set_read_only(content['read_only'])

    def on_action_validate(self, content):
        """ Handle the 'validate' action from the Enaml widget.

        """
        if self.dirty:
            validators = self.validators.get('all')
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
                self._validation_failure(orig, text, info)
                return

        # Everything validated, we need to send the text update to
        # the Enaml widget and update the control if the validators 
        # have changed the text.
        if orig != text:
            pos = self.widget.cursorPosition()
            self.widget.setText(text)
            self.widget.setCursorPosition(pos)

        content = {'text': text}
        self.send_action('text_changed', content)
        self.dirty = False

    def _validation_failure(self, orig, text, info):
        """ Handle a validator failing its validation.

        """
        # This is just a temporary popup hack for now until we get 
        # Naveen's pretty popup widget in place.
        msg = info.get('action', '')
        msg = 'Validation Failure: %s' % msg
        widget = self.widget
        globalPos = widget.mapToGlobal(widget.pos())
        QWhatsThis.showText(globalPos, msg, widget)
        QTimer.singleShot(2000, QWhatsThis.hideText)

