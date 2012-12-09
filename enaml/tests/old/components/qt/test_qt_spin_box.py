#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_test_assistant import QtTestAssistant
from .. import spin_box


class TestQtSpinBox(QtTestAssistant, spin_box.TestSpinBox):
    """ QtSpinBox tests. """

    def get_value(self, widget):
        """ Get a spin box's value.

        """
        return widget.value()

    def get_low(self, widget):
        """ Get a spin box's minimum value.

        """
        return widget.minimum()

    def get_high(self, widget):
        """ Get a spin box's maximum value.

        """
        return widget.maximum()

    def get_step(self, widget):
        """ Get a spin box's step size.

        """
        return widget.singleStep()

    def get_wrap(self, widget):
        """ Check if a spin box wraps around at the edge values.

        """
        return widget.wrapping()

    def get_text(self, widget):
        """ Get the text displayed in a spin box.

        """
        return widget.text()

    def spin_up_event(self, widget):
        """ Simulate a click on the 'up' spin button.

        """
        widget.stepUp()

    def spin_down_event(self, widget):
        """ Simulate a click on the 'down' spin button.

        """
        widget.stepDown()
