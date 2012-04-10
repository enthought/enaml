#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QSpinBox, QValidator
from .qt_control import QtControl

from ...components.spin_box import AbstractTkSpinBox


class EnamlQSpinBox(QSpinBox):
    """ A QSpinBox sublcass with hooks for user supplied validation.

    """
    #: The internal storage for the Enaml validator object. 
    _validator = None

    def validator(self):
        """ Returns the Enaml validator assigned to this spin box.

        """
        return self._validator
    
    def setValidator(self, validator):
        """ Set the validator for this spin box.

        """
        self._validator = validator
        self.interpretText()

    def textFromValue(self, value):
        """ Converts the given integer to a string for display using the 
        user supplied validator object. 

        If the conversion fails due to the converter raising a ValueError
        then simple unicode(...) conversion is used.

        """
        try:
            text = self._validator.format(value)
        except ValueError:
            text = unicode(value)
        return text

    def valueFromText(self, text):
        """ Converts the user typed string into an integer for the
        control using the user supplied validator.

        """
        return self._validator.convert(text)

    def validate(self, text, pos):
        """ Validates whether or not the given text can be converted
        to an integer.

        """
        v = self._validator
        rv = v.validate(text)
        if rv == v.ACCEPTABLE:
            res = QValidator.Acceptable
        elif rv == v.INTERMEDIATE:
            res = QValidator.Intermediate
        elif rv == v.INVALID:
            res = QValidator.Invalid
        else:
            # This should never happen
            raise ValueError('Invalid validation result')
        return (res, text, pos)


class QtSpinBox(QtControl, AbstractTkSpinBox):
    """ A Qt implementation of SpinBox.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying custom spin control.

        """
        self.widget = EnamlQSpinBox(parent)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtSpinBox, self).initialize()
        shell = self.shell_obj
        self.set_validator(shell.validator)
        self.set_spin_low(shell.low)
        self.set_spin_high(shell.high)
        self.set_spin_step(shell.step)
        self.set_spin_value(shell.value)
        self.set_spin_wrap(shell.wrap)
        self.set_spin_tracking(shell.tracking)

    def bind(self):
        """ Binds the event handlers for the spin control.

        """
        super(QtSpinBox, self).bind()
        self.widget.valueChanged.connect(self.on_value_changed)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_value_changed(self, value):
        """ The change handler for the 'value' attribute of the shell
        object.

        """
        self.set_spin_value(value)

    def shell_low_changed(self, low):
        """ The change handler for the 'low' attribute of the shell
        object.

        """
        self.set_spin_low(low)

    def shell_high_changed(self, high):
        """ The change handler for the 'high' attribute of the shell
        object.

        """
        self.set_spin_high(high)

    def shell_step_changed(self, step):
        """ The change handler for the 'step' attribute of the shell
        object.

        """
        self.set_spin_step(step)

    def shell_validator_changed(self, validator):
        """ The change handler for the 'validator' attribute of the shell
        object.

        """
        self.set_validator(validator)

    def shell_wrap_changed(self, wrap):
        """ The change handler for the 'wrap' attribute of the shell 
        object.

        """
        self.set_spin_wrap(wrap)

    def shell_tracking_changed(self, tracking):
        """ The change handler for the 'tracking' attribute of the shell
        object.

        """
        self.set_spin_tracking(tracking)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_value_changed(self):
        """ The event handler for the widget's spin event.

        """
        self.shell_obj.value = self.widget.value()

    #--------------------------------------------------------------------------
    # Widget update methods 
    #--------------------------------------------------------------------------
    def set_spin_value(self, value):
        """ Sets the value of the widget.

        """
        self.widget.setValue(value)

    def set_spin_low(self, low):
        """ Sets the minimum value of the widget.

        """
        self.widget.setMinimum(low)

    def set_spin_high(self, high):
        """ Sets the maximum value of the widget.

        """
        self.widget.setMaximum(high)

    def set_spin_step(self, step):
        """ Sets the step size of the widget.

        """
        self.widget.setSingleStep(step)

    def set_validator(self, validator):
        """ Sets the validator for the widget.

        """
        self.widget.setValidator(validator)

    def set_spin_wrap(self, wrap):
        """ Sets the wrap mode of the widget.

        """
        self.widget.setWrapping(wrap)

    def set_spin_tracking(self, tracking):
        """ Sets the keyboard tracking of the widget.

        """
        self.widget.setKeyboardTracking(tracking)

