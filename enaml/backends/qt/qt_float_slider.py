#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_slider import QtSlider

from ..float_slider import AbstractTkFloatSlider



class QtFloatSlider(QtSlider, AbstractTkFloatSlider):
    """ A Qt implementation of FloatSlider.

    """
    def initialize(self):
        """ Initializes the attributes of the toolkit widget.

        """
        shell = self.shell_obj
        shell._down = False
        self.set_precision(shell.precision)
        super(QtFloatSlider, self).initialize()

    def bind(self):
        """ Connect the event handlers for the slider widget signals.

        """
        super(QtSlider, self).bind()
        widget = self.widget
        widget.valueChanged.connect(self._on_slider_changed)
        widget.sliderMoved.connect(self._on_slider_moved)
        widget.sliderPressed.connect(self._on_pressed)
        widget.sliderReleased.connect(self._on_released)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------

    def shell_precision_changed(self, precision):
        """ The change handler for the 'precision' attribute on the shell
        object.
        
        """
        self.set_precision(precision)

    #--------------------------------------------------------------------------
    # Event Handlers 
    #--------------------------------------------------------------------------
    def _on_slider_changed(self):
        """ The event handler for the slider value changed event.

        """
        self.shell_obj.value = self.int_to_float(self.widget.value())

    def _on_slider_moved(self):
        """ The event handler for a slider moved event.

        """
        self.shell_obj.moved(self.int_to_float(self.widget.sliderPosition()))

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_precision(self, precision):
        """ Set the precision attribute in the Qt widget.

        """
        self.widget.setRange(0, precision)

    def set_range(self, minimum, maximum):
        """ Set the range of the slider widget.

        Overridden to ignore the float values. The Qt widget knows nothing about
        them.

        """
        pass

    def set_position(self, value):
        """ Validate the position value.

        """
        self.widget.setValue(self.float_to_int(value))

    def float_to_int(self, value):
        """ Convert a float value to an int value.

        """
        shell = self.shell_obj
        u = (value - shell.minimum) / (shell.maximum - shell.minimum)
        i = int(round(u * shell.precision))
        return i

    def int_to_float(self, value):
        """ Convert an int value to a float value.

        """
        shell = self.shell_obj
        u = float(value) / shell.precision
        x = u * shell.maximum + (1.0-u) * shell.minimum
        return x
