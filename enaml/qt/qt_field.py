#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
import re

from .qt.QtGui import QLineEdit, QWhatsThis
from .qt.QtCore import Signal, QTimer
from .qt_constraints_widget import QtConstraintsWidget


ECHO_MODES = {
    'normal': QLineEdit.Normal,
    'password' : QLineEdit.Password,
    'silent' : QLineEdit.NoEcho
}


class AbstractValidator(object):
    """ An abstract base class which defines the api for creating a 
    field validator.

    """
    __metaclass__ = ABCMeta

    def __init__(self, info):
        """ Initialize a validator.

        Parameters
        ----------
        info : dict
            The validator info dict sent over by the Enaml widget.

        """
        self.info = info

    @abstractmethod
    def validate(self, text):
        """ Validate the text as valid input.

        This method should check the text against the internal rules
        of the validator. If the text is acceptable, the validator
        should return the text (optionally modified). If the text
        is not acceptable, it should raise a ValueError.

        Parameters
        ----------
        text : unicode
            The unicode text to validate.

        Returns
        -------
        result : unicode
            The (optionally modified) acceptable text.

        Raises
        ------
        ValueError
            A ValueError will be raised if the text does not validate.

        """
        raise NotImplementedError


class NullValidator(AbstractValidator):
    """ A concrete validator which accepts all input values.

    """
    def validate(self, text):
        return text


class RegexpValidator(AbstractValidator):
    """ A concrete validator based on a regular expression matching.

    """
    def __init__(self, info):
        super(RegexpValidator, self).__init__(info)
        self.regexp = re.compile(info['regexp'], re.UNICODE)

    def validate(self, text):
        if self.regexp.match(text):
            return text
        raise ValueError


VALIDATORS = {
    'null': NullValidator,
    'regexp': RegexpValidator,
}


def parse_validators(validators):
    res = {'all': []}
    for info in validators:
        vldr_cls = VALIDATORS.get(info['type'])
        if vldr_cls is not None:
            vldr = vldr_cls(info)
            res['all'].append(vldr)
            triggers = info['triggers']
            if triggers:
                for trigger in triggers:
                    if trigger not in res:
                        res[trigger] = []
                    res[trigger].append(vldr)
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
    def on_message_set_text(self, payload):
        """ Handle the 'set-text' action from the Enaml widget.

        """
        self.set_text(payload['text'])

    def on_message_set_validators(self, payload):
        """ Handle the 'set-validators' action from the Enaml widget.

        """
        self.validators = parse_validators(payload['validators'])

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
        for validator in validators:
            try:
                text = validator.validate(text)
            except ValueError:
                self._validation_failure(orig, text, validator)
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
        self.dirty = False

    def _validation_failure(self, orig, text, validator):
        """ Handle a validator failing its validation.

        """
        # This is just a temporary popup hack for now until we get 
        # Naveen's pretty popup widget in place.
        info = validator.info
        msg = info.get('message', '')
        msg = 'Validation Failure: %s' % msg
        widget = self.widget
        globalPos = widget.mapToGlobal(widget.pos())
        QWhatsThis.showText(globalPos, msg, widget)
        QTimer.singleShot(2000, QWhatsThis.hideText)

