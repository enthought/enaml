#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_control import QtControl

from ..spin_box import AbstractTkSpinBox

from ...converters import IntConverter


class EnamlQSpinBox(QtGui.QSpinBox):
    """ A QSpinBox with hooks for user-supplied string conversion.

    """
    #: The internal storage for the Enaml converter object. 
    #: The default converter is an IntConverter.
    _converter = IntConverter()

    def converter(self):
        """ Returns the converter assigned to this spin box.

        """
        return self._converter
    
    def setConverter(self, converter):
        """ Set the converter for this spin box.

        """
        self._converter = converter
        self.interpretText()

    def textFromValue(self, value):
        """ Converts the given integer to a string for display using the 
        user supplied converter object. 

        If the conversion fails due to the converter raising a ValueError
        then simple str(...) conversion is used.

        """
        try:
            text = self._converter.to_component(value)
        except ValueError:
            text = str(value)
        return text

    def valueFromText(self, text):
        """ Converts the user typed string into an integer for the
        control using the user supplied converter.

        """
        # Qt will only call this method if the validate method has 
        # returned Acceptable, so we can safetly assume that calling 
        # the converter again will not raise an error. Further, we don't 
        # worry too much about calling the converter twice since it 
        # should be a relatively cheap operation to convert a string to 
        # some int. If it's not, then a given converter can implement its
        # own internal caching to speed things up.
        return self._converter.from_component(text)

    def validate(self, text, pos):
        """ Validates whether or not the given text can be converted
        to an integer.

        """
        # Note that we avoid returning an Invalid QValidator value
        # since that prevents the control from accepting that keystroke
        # and makes the ui a bit cumbersome to use.
        try:
            val = self._converter.from_component(text)
        except ValueError:
            res = QtGui.QValidator.Intermediate
        else:
            if self.minimum() <= val <= self.maximum():
                res = QtGui.QValidator.Acceptable
            else:
                res = QtGui.QValidator.Intermediate
        return res


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
        self.set_spin_low(shell.low)
        self.set_spin_high(shell.high)
        self.set_spin_step(shell.step)
        self.set_spin_converter(shell.converter)
        self.set_spin_wrap(shell.wrap)
        self.set_spin_value(shell.value)
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

    def shell_converter_changed(self, converter):
        """ The change handler for the 'converter' attribute of the shell
        object.

        """
        self.set_spin_converter(converter)

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

    def set_spin_converter(self, converter):
        """ Sets the coverter for the widget.

        """
        self.widget.setConverter(converter)

    def set_spin_wrap(self, wrap):
        """ Sets the wrap mode of the widget.

        """
        self.widget.setWrapping(wrap)

    def set_spin_tracking(self, tracking):
        """ Sets the keyboard tracking of the widget.

        """
        self.widget.setKeyboardTracking(tracking)

