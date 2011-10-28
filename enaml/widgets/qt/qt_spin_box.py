#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from logging import exception

from .qt import QtGui

from .qt_control import QtControl

from ..spin_box import AbstractTkSpinBox

_QtValidate = {
    'invalid': QtGui.QValidator.Invalid,
    'intermediate': QtGui.QValidator.Intermediate,
    'acceptable': QtGui.QValidator.Acceptable
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


class QtSpinBox(QtControl, AbstractTkSpinBox):
    """ A Qt implementation of SpinBox.

    See Also
    --------
    SpinBox

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying custom spin control.

        """
        self.widget = EnamlQSpinBox(self.parent_widget())

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtSpinBox, self).initialize()
        shell = self.shell_obj
        self.set_spin_low(shell.low)
        self.set_spin_high(shell.high)
        self.set_spin_step(shell.step)
        self.set_spin_prefix(shell.prefix)
        self.set_spin_suffix(shell.suffix)
        self.set_spin_special_value_text(shell.special_value_text)
        self.set_spin_converter(shell.converter)
        self.set_spin_validate_string(shell.validate_string)
        self.set_spin_wrap(shell.wrap)
        self.set_spin_value(shell.value)
        self.bind()

    def bind(self):
        """ Binds the event handlers for the spin control.

        """
        super(QtSpinBox, self).bind()
        self.widget.valueChanged.connect(self.on_value_changed)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_value_changed(self, value):
        """ The change handler for the 'value' attribute. Not meant
        for public consumption.

        """
        self.set_spin_value(value)

    def shell_low_changed(self, low):
        """ The change handler for the 'low' attribute. Not meant
        for public consumption.

        """
        self.set_spin_low(low)

    def shell_high_changed(self, high):
        """ The change handler for the 'high' attribute. Not meant
        for public consumption.

        """
        self.set_spin_high(high)

    def shell_step_changed(self, step):
        """ The change handler for the 'step' attribute. Not meant
        for public consumption.

        """
        self.set_spin_step(step)

    def shell_prefix_changed(self, prefix):
        """ The change handler for the 'prefix' attribute. Not meant
        for public consumption.

        """
        self.set_spin_prefix(prefix)

    def shell_suffix_changed(self, suffix):
        """ The change handler for the 'suffix' attribute. Not meant
        for public consumption.

        """
        self.set_spin_suffix(suffix)

    def shell_special_value_text_changed(self, text):
        """ The change handler for the 'special_value_text' attribute.
        Not meant for public consumption.

        """
        self.set_spin_special_value_text(text)

    def shell_converter_changed(self, converter):
        """ The change handler for the 'converter' attribute. Not meant
        for public consumption.

        """
        self.set_spin_converter(converter)

    def shell_validate_string_changed(self, validate_string):
        """ The change handler for the 'validate_string' attribute. Not meant
        for public consumption.

        """
        self.set_spin_validate_string(validate_string)

    def shell_wrap_changed(self, wrap):
        """ The change handler for the 'wrap' attribute. Not meant for
        public consumption.

        """
        self.set_spin_wrap(wrap)

    def on_value_changed(self):
        """ The event handler for the widget's spin event. Not meant
        for public consumption.

        """
        self.shell_obj.value = self.widget.value()

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
        self.widget.setValue(self.shell_obj.value)

    def set_spin_suffix(self, suffix):
        """ Updates the suffix of the spin box. Not meant for public
        consumption.

        """
        self.widget.setSuffix(suffix)
        self.widget.setValue(self.shell_obj.value)

    def set_spin_special_value_text(self, text):
        """ Updates the special value text of the spin box. Not meant
        for public consumption.

        """
        self.widget.setSpecialValueText(text)

    def set_spin_converter(self, converter):
        """ Updates the 'to_string' and 'from_string' functions of the
        spin box. Not meant for public consumption.

        """
        self.widget.from_string = converter.from_component
        self.widget.to_string = converter.to_component
        self.widget.setValue(self.shell_obj.value)

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

