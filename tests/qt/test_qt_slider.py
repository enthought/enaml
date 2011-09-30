#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.widgets.qt.qt import QtGui, QtCore

from ..common import slider
from enaml.toolkit import qt_toolkit
from enaml.enums import TickPosition, Orientation
from enaml.widgets.qt.qt_slider import SLIDER_MAX

# A map from QSlider TickPosition values to Enaml constants.
TICK_POS_MAP = {QtGui.QSlider.NoTicks: TickPosition.DEFAULT,
                QtGui.QSlider.TicksLeft: TickPosition.LEFT,
                QtGui.QSlider.TicksRight: TickPosition.RIGHT,
                QtGui.QSlider.TicksAbove: TickPosition.TOP,
                QtGui.QSlider.TicksBelow: TickPosition.BOTTOM,
                QtGui.QSlider.TicksBothSides: TickPosition.BOTH,
                QtGui.QSlider.NoTicks: TickPosition.NO_TICKS}

# A map from Qt constants for horizontal or vertical orientation to Enaml enums.
ORIENTATION_MAP = {QtCore.Qt.Horizontal: Orientation.HORIZONTAL,
                   QtCore.Qt.Vertical: Orientation.VERTICAL}


# Map test event actions to the Qt Slider event signals
EVENT_MAP = {slider.TestEvents.PRESSED: 'sliderPressed',
             slider.TestEvents.RELEASED: 'sliderReleased'}

# Map test event actions to the Qt Slider actions
ACTION_MAP ={slider.TestEvents.HOME: QtGui.QAbstractSlider.SliderToMinimum,
             slider.TestEvents.END: QtGui.QAbstractSlider.SliderToMaximum,
             slider.TestEvents.STEP_UP: QtGui.QAbstractSlider.SliderSingleStepAdd,
             slider.TestEvents.STEP_DOWN: QtGui.QAbstractSlider.SliderSingleStepSub,
             slider.TestEvents.PAGE_UP: QtGui.QAbstractSlider.SliderPageStepAdd,
             slider.TestEvents.PAGE_DOWN: QtGui.QAbstractSlider.SliderPageStepSub}

class TestQtSlider(slider.TestSlider):
    """ QtLabel tests. """

    toolkit = qt_toolkit()

    def get_value(self, widget):
        """ Get a slider's position.

        """
        value = float(widget.value())
        return self.component.from_slider(value / SLIDER_MAX)

    def get_tick_interval(self, widget):
        """ Get the Slider's tick_interval value.

        """
        value = float(widget.tickInterval())
        return value / SLIDER_MAX

    def get_tick_position(self, widget):
        """ Get the Slider's tick position style.

        """
        value = widget.tickPosition()
        return TICK_POS_MAP[value]

    def get_orientation(self, widget):
        """ Get the Slider's orientation.

        """
        value = widget.orientation()
        return ORIENTATION_MAP[value]

    def get_single_step(self, widget):
        """ Get the Slider's single step value.

        """
        value = widget.singleStep() / widget.tickInterval()
        return value

    def get_page_step(self, widget):
        """ Get the Slider's page step value.

        """
        value = widget.pageStep() / widget.tickInterval()
        return value

    def get_tracking(self, widget):
        """ Get the Slider's tracking status.

        """
        return widget.hasTracking()

    def sent_event(self, widget, event):
        """ Sent an event to the Slider programmatically.

        Arguments
        ---------
        widget :
            The widget to sent the event to.

        event :
            The desired event to be proccessed.

        """
        if event in ACTION_MAP:
            widget.triggerAction(ACTION_MAP[event])
        elif event in EVENT_MAP:
            getattr(widget, EVENT_MAP[event]).emit()
        else:
            raise NotImplementedError('Test event is not Implemented')

