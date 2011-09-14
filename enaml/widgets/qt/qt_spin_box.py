from logging import exception

from .qt import QtGui

from traits.api import implements

from .qt_control import QtControl

from ...enums import Validity

from ..spin_box import ISpinBoxImpl

_QtValidate = {
    Validity.INVALID: QtGui.QValidator.Invalid,
    Validity.INTERMEDIATE: QtGui.QValidator.Intermediate,
    Validity.ACCEPTABLE: QtGui.QValidator.Acceptable
}


class EnamlQSpinBox(QtGui.QSpinBox):
    """ A QSpinBox with hooks for user-supplied string conversion
    """
    
    #: conversion callable that converts values to strings (default is `str`)
    to_string = str
    
    #: conversion callable that converts strings to values (default is `int`)
    from_string = int
    
    #: validator callable that validates strings (default is to try from_string)
    validate_string = None
    
    def textFromValue(self, value):
        """ Delegate text conversion to callable attribute
        """
        try:
            text = self.to_string(value)
        except Exception, e:
            exception(e)
            text = str(value)
        return text
    
    def valueFromText(self, text):
        """ Delegate text conversion to callable attribute
        """
        try:
            value = self.from_string(text)
        except Exception, e:
            exception(e)
            value = self.value
        return value
    
    def validate(self, text, int):
        """ Validate the text.
        
        By default try to see if from_string() works, if it fails then state is
        'intermediate'.  If we have a validate_string method, then we call that
        instead.
        """
        if callable(self.validate_string):
            return _QtValidate[self.validate_string(text)]

        try:
            self.from_string(text)
            return QtGui.QValidator.Acceptable
        except Exception, e:
            return QtGui.QValidator.Intermediate


class QtSpinBox(QtControl):
    """ A Qt implementation of SpinBox.

    See Also
    --------
    SpinBox

    """
    implements(ISpinBoxImpl)

    def create_widget(self):
        """ Creates the underlying custom spin control.

        """
        self.widget = EnamlQSpinBox(self.parent_widget())

    def initialize_widget(self):
        """ Intializes the widget with the attributes of this instance.

        """
        parent = self.parent
        self.set_spin_low(parent.low)
        self.set_spin_high(parent.high)
        self.set_spin_step(parent.step)
        self.set_spin_prefix(parent.prefix)
        self.set_spin_suffix(parent.suffix)
        self.set_spin_special_value_text(parent.special_value_text)
        self.set_spin_to_string(parent.to_string)
        self.set_spin_from_string(parent.from_string)
        self.set_spin_validate_string(parent.validate_string)
        self.set_spin_wrap(parent.wrap)
        self.set_spin_value(parent.value)
        self.bind()

    def parent_value_changed(self, value):
        """ The change handler for the 'value' attribute. Not meant
        for public consumption.

        """
        self.set_spin_value(value)

    def parent_low_changed(self, low):
        """ The change handler for the 'low' attribute. Not meant
        for public consumption.

        """
        self.set_spin_low(low)

    def parent_high_changed(self, high):
        """ The change handler for the 'high' attribute. Not meant
        for public consumption.
        
        """
        self.set_spin_high(high)
    
    def parent_step_changed(self, step):
        """ The change handler for the 'step' attribute. Not meant
        for public consumption.
        
        """
        self.set_spin_step(step)
    
    def parent_prefix_changed(self, prefix):
        """ The change handler for the 'prefix' attribute. Not meant
        for public consumption.
        
        """
        self.set_spin_prefix(prefix)
    
    def parent_suffix_changed(self, suffix):
        """ The change handler for the 'suffix' attribute. Not meant
        for public consumption.

        """
        self.set_spin_suffix(suffix)
    
    def parent_special_value_text_changed(self, text):
        """ The change handler for the 'special_value_text' attribute.
        Not meant for public consumption.
        
        """
        self.set_spin_special_value_text(text)
    
    def parent_to_string_changed(self, to_string):
        """ The change handler for the 'to_string' attribute. Not meant
        for public consumption.
        
        """
        self.set_spin_to_string(to_string)
    
    def parent_from_string_changed(self, from_string):
        """ The change handler for the 'from_string' attribute. Not meant 
        for public consumption.
        
        """
        self.set_spin_from_string(from_string)
    
    def parent_validate_string_changed(self, validate_string):
        """ The change handler for the 'validate_string' attribute. Not meant 
        for public consumption.
        
        """
        self.set_spin_validate_string(validate_string)
    
    def parent_wrap_changed(self, wrap):
        """ The change handler for the 'wrap' attribute. Not meant for
        public consumption.
        
        """
        self.set_spin_wrap(wrap)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def bind(self):
        """ Binds the event handlers for the spin control.

        """
        self.widget.valueChanged.connect(self.on_value_changed)

    def on_value_changed(self):
        """ The event handler for the widget's spin event. Not meant
        for public consumption.

        """
        self.parent.value = self.widget.value()

    def set_spin_value(self, value):
        """ Updates the widget with the given value. Not meant for 
        public consumption.

        """
        self.widget.setValue(value)

    def set_spin_low(self, low):
        """ Updates the low limit of the spin box. Not meant for 
        public consumption.

        """
        self.widget.setMinimum(low)
    
    def set_spin_high(self, high):
        """ Updates the high limit of the spin box. Not meant for 
        public consumption.

        """
        self.widget.setMaximum(high)
    
    def set_spin_step(self, step):
        """ Updates the step of the spin box. Not meant for public
        consumption.

        """
        self.widget.setSingleStep(step)
    
    def set_spin_prefix(self, prefix):
        """ Updates the prefix of the spin box. Not meant for public
        consumption.

        """
        self.widget.setPrefix(prefix)
        self.widget.setValue(self.parent.value)

    def set_spin_suffix(self, suffix):
        """ Updates the suffix of the spin box. Not meant for public
        consumption.

        """
        self.widget.setSuffix(suffix)
        self.widget.setValue(self.parent.value)

    def set_spin_special_value_text(self, text):
        """ Updates the special value text of the spin box. Not meant
        for public consumption.

        """
        self.widget.setSpecialValueText(text)
    
    def set_spin_to_string(self, to_string):
        """ Updates the to_string function of the spin box. Not meant
        for public consumption.

        """
        self.widget.to_string = to_string
        self.widget.setValue(self.parent.value)
    
    def set_spin_from_string(self, from_string):
        """ Updates the from_string function of the spin box. Not meant
        for public consumption.

        """
        self.widget.from_string = from_string
    
    def set_spin_validate_string(self, validate_string):
        """ Updates the validate_string function of the spin box. Not meant
        for public consumption.

        """
        self.widget.validate_string = validate_string
    
    def set_spin_wrap(self, wrap):
        """ Updates the wrap value of the spin box. Not meant for public
        consumption.

        """
        self.widget.setWrapping(wrap)

