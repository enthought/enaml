#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.widgets.qt.qt import QtGui, QtCore

from enaml.widgets.qt.qt_slider import (HOR_TICK_POS_MAP,
                                        VERT_TICK_POS_MAP)

from .qt_test_assistant import QtTestAssistant
from .. import slider

# A map from Qt constants for horizontal or vertical orientation to Enaml enums.
ORIENTATION_MAP = {QtCore.Qt.Horizontal: 'horizontal',
                   QtCore.Qt.Vertical: 'vertical'}


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

class TestQtSlider(QtTestAssistant, slider.TestSlider):
    """ QtLabel tests. """

    def get_value(self, widget):
        """ Get a slider's position.

        """
        return widget.value()

    def get_minimum(self, widget):
        """ Get the Slider's minimum value.

        """
        return widget.minimum()

    def get_maximum(self, widget):
        """ Get the Slider's maximum value.

        """
        return widget.maximum()

    def get_tick_interval(self, widget):
        """ Get the Slider's tick_interval value.

        """
        return widget.tickInterval()

    def get_tick_position(self, widget):
        """ Get the Slider's tick position style.

        """
        value = widget.tickPosition()
        orientation = self.get_orientation(widget)
        if orientation == 'vertical':
            result = VERT_TICK_POS_MAP[value]
        else:
            result = HOR_TICK_POS_MAP[value]
        return result

    def get_orientation(self, widget):
        """ Get the Slider's orientation.

        """
        value = widget.orientation()
        return ORIENTATION_MAP[value]

    def get_single_step(self, widget):
        """ Get the Slider's single step value.

        """
        return widget.singleStep()

    def get_page_step(self, widget):
        """ Get the Slider's page step value.

        """
        return widget.pageStep()

    def get_tracking(self, widget):
        """ Get the Slider's tracking status.

        """
        return widget.hasTracking()

    def send_event(self, widget, event):
        """ Send an event to the Slider programmatically.

        Arguments
        ---------
        widget :
            The widget to send the event to.

        event :
            The desired event to be proccessed.

        """
        if event in ACTION_MAP:
            widget.triggerAction(ACTION_MAP[event])
        elif event in EVENT_MAP:
            getattr(widget, EVENT_MAP[event]).emit()
        else:
            raise NotImplementedError('Test event is not Implemented')

