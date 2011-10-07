#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore

from traits.api import implements, Float, Int, Tuple

from .qt_control import QtControl

from ..slider import ISliderImpl

from ...enums import Orientation, TickPosition


# Constant value for conversion between Range(0, 1.0) and integers.
SLIDER_MAX = 10000

# A map from Enaml constants to QSlider TickPosition values.
TICK_POS_MAP = {TickPosition.DEFAULT: QtGui.QSlider.NoTicks,
                TickPosition.LEFT: QtGui.QSlider.TicksLeft,
                TickPosition.RIGHT: QtGui.QSlider.TicksRight,
                TickPosition.TOP: QtGui.QSlider.TicksAbove,
                TickPosition.BOTTOM: QtGui.QSlider.TicksBelow,
                TickPosition.BOTH: QtGui.QSlider.TicksBothSides,
                TickPosition.NO_TICKS: QtGui.QSlider.NoTicks}

# A map from Enaml enums to Qt constants for horizontal or vertical orientation.
ORIENTATION_MAP = {Orientation.HORIZONTAL: QtCore.Qt.Horizontal,
                   Orientation.VERTICAL: QtCore.Qt.Vertical}


# Qt Slider does not return TicksLeft and TicksRight it always
# converts these to TicksAbove and TicksBelow so we need to check
# the orientation in order to return the right result

# A map from horizontal QSlider TickPosition values to Enaml constants.
HOR_TICK_POS_MAP = {QtGui.QSlider.NoTicks: TickPosition.DEFAULT,
                    QtGui.QSlider.TicksAbove: TickPosition.TOP,
                    QtGui.QSlider.TicksBelow: TickPosition.BOTTOM,
                    QtGui.QSlider.TicksBothSides: TickPosition.BOTH,
                    QtGui.QSlider.NoTicks: TickPosition.NO_TICKS}

# A map from vertical QSlider TickPosition values to Enaml constants.
VERT_TICK_POS_MAP = {QtGui.QSlider.NoTicks: TickPosition.DEFAULT,
                    QtGui.QSlider.TicksAbove: TickPosition.LEFT,
                    QtGui.QSlider.TicksBelow: TickPosition.RIGHT,
                    QtGui.QSlider.TicksBothSides: TickPosition.BOTH,
                    QtGui.QSlider.NoTicks: TickPosition.NO_TICKS}



class QtSlider(QtControl):
    """ A Qt implementation of Slider.

    See Also
    --------
    Slider

    """
    implements(ISliderImpl)

    #---------------------------------------------------------------------------
    # ISliderImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying QSlider widget.

        """
        self.widget = QtGui.QSlider(parent=self.parent_widget())

    def initialize_widget(self):
        """ Initializes the attributes of the toolkit widget.

        """
        parent = self.parent
        parent._down = False

        # We hard-coded range for the widget since we are managing the
        # conversion.
        self.set_range(0, SLIDER_MAX)
        self.set_and_validate_position(parent.value)
        self.set_orientation(parent.orientation)
        self.set_tick_position(parent.tick_position)
        self.set_tick_frequency(parent.tick_interval)
        self.set_single_step(parent.single_step)
        self.set_page_step(parent.page_step)
        self.set_tracking(parent.tracking)

        self.connect()

    def parent_converter_changed(self, converter):
        """ Update the slider when the converter class changes.

        """
        pass

    def parent_value_changed(self, value):
        """ Update the slider position

        The method validates the value before assigment. If it is out of
        range (0.0, 1.0), truncate the value and updates the component value
        attribute. No change notification is fired by these actions.

        If other exceptions are fired during the assigments the component
        value does not change and the widget position is unknown.

        """
        parent = self.parent
        self.set_and_validate_position(value)
        validated_value = self.get_position()
        parent.trait_setq(value=validated_value)
        self.parent.moved = validated_value


    def parent_tracking_changed(self, tracking):
        """ Set the tracking event in the widget

        """
        self.set_tracking(tracking)

    def parent_single_step_changed(self, single_step):
        """ Update the the line step in the widget.

        """
        self.set_single_step(single_step)

    def parent_page_step_changed(self, page_step):
        """ Update the widget due to change in the line step.

        """
        self.set_page_step(page_step)

    def parent_tick_interval_changed(self, tick_interval):
        """ Update the tick marks interval.

        """
        parent = self.parent
        self.set_tick_frequency(tick_interval)
        self.set_single_step(parent.single_step)
        self.set_page_step(parent.page_step)

    def parent_tick_position_changed(self, tick_position):
        """ Update the widget due to change in the tick position

        The method ensures that the tick position style can be applied
        and reverts to the last value if the request is invalid.

        """
        self.set_tick_position(tick_position)

    def parent_orientation_changed(self, orientation):
        """ Update the widget due to change in the orientation attribute

        The method applies the orientation style and fixes the tick position
        option if necessary.

        """
        self.set_orientation(orientation)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------

    def connect(self):
        """ connect the event handlers for the slider widget signals.

        """
        widget = self.widget
        widget.valueChanged.connect(self._on_slider_changed)
        widget.sliderPressed.connect(self._on_pressed)
        widget.sliderReleased.connect(self._on_released)


    def _on_slider_changed(self, value):
        """ Respond to a (possible) change in value from the ui.

        """
        parent = self.parent
        new_value = self.get_position()
        parent.value = new_value

    def _on_pressed(self):
        """ Update if the left button was pressed.

        Estimates the position of the thumb and then checks if the mouse
        was pressed over it to fire the `pressed` event and sets the
        `down` attribute.

        """
        parent = self.parent
        parent._down = True
        parent.pressed = True

    def _on_released(self):
        """ Update if the left button was released

        Checks if the `down` attribute was set. In that case the
        function fires the release event and sets the `down` attribute to
        false.

        """
        parent = self.parent
        if parent._down:
            parent._down = False
            parent.released = True

    def set_single_step(self, step):
        """ Set the single step attribute in the Qt widget.

        Arguments
        ---------
        step: int
            the number of steps (in tick intervals) to move the slider
            when the user uses the arrow keys.

        """
        widget = self.widget
        tick_interval = widget.tickInterval()
        widget.setSingleStep(step * tick_interval)

    def set_page_step(self, step):
        """ Set the page step attribute in the Qt widget.

        Arguments
        ---------
        step: int
            The number of steps (in tick intervals) to move the slider
            when the user uses the page-up / page-down key. This is also
            used when the user clicks on the left or the right of the
            thumb.

        """
        widget = self.widget
        tick_interval = widget.tickInterval()
        widget.setPageStep(step * tick_interval)

    def set_tick_position(self, ticks):
        """ Apply the tick position in the widget.

        The tick_position is addapted to reflect the current orientation.
        This is agrees with how the QSlider is behaving.

        Arguments
        ---------
        ticks : TickPosition
            The tick position.
        """
        parent = self.parent

        constant = TICK_POS_MAP[ticks]
        self.widget.setTickPosition(constant)

        self.sync_tick_position()


    def set_orientation(self, orientation):
        """ Set the slider orientation

        Arguments
        ---------
        orientation : Orientation
            The orientation of the slider.

        """
        widget = self.widget
        parent = self.parent
        tick_position = parent.tick_position

        constant = ORIENTATION_MAP[orientation]
        self.widget.setOrientation(constant)

        self.sync_tick_position()

    def set_tracking(self, tracking):
        """ Receive a 'valueChanged' signal when the slider is dragged.

        Arguments
        ---------
        tracking : boolean
            When true the event is bound to the enaml class

        """
        self.widget.setTracking(tracking)

    def set_range(self, minimum, maximum):
        """ Set the slider widget range

        Arguments
        ---------
        minimum : int
            The minimum value

        maximum : int
            The maximum value

        """
        self.widget.setRange(minimum, maximum)

    def set_tick_frequency(self, interval):
        """ Set the slider widget tick marg fequency

        Arguments
        ---------
        interval: float
            The step size for tick marks.

        """
        self.widget.setTickInterval(interval * SLIDER_MAX)

    def set_and_validate_position(self, value):
        """ Validate the position value.

        The method checks if the value that can be converted to float and
        is in the range of [0.0, 1.0]. If the validation is not succesful
        it sets the `error` and `exception` attributes and truncates the
        assing value in range.

        """
        parent = self.parent
        self.reset_errors()

        try:
            position = parent.converter.to_component(value)
            self.widget.setValue(position * SLIDER_MAX)
            if not (0.0 <= position <= 1.0):
                raise ValueError('to_widget() must return a value'
                                 ' between 0.0 and 1.0, but instead'
                                 ' returned %s'  % repr(position))
        except Exception as raised_exception:
            self.notify(raised_exception)

    def get_position(self):
        """ Get the slider position from the widget.

        If error occurs during the conversion it is recorded in the
        `error` and `exception` attributes. The return value in that case
        is None since the value is undefined.

        """
        parent = self.parent
        value = None
        try:
            position = self.widget.value() / float(SLIDER_MAX)
            value = parent.converter.from_component(position)
        except Exception as raised_exception:
            self.notify(raised_exception)
        return value

    def sync_tick_position(self):
        """ Syncornize the tick_position with the widget

        The QSlider automatically updates or adaptes the tick position but
        we still need to update the enaml component, so that it is in sync.

        """
        parent = self.parent
        orientation = parent.orientation
        tick_pos = self.widget.tickPosition()

        if orientation == Orientation.VERTICAL:
            parent.tick_position = VERT_TICK_POS_MAP[tick_pos]
        else:
            parent.tick_position = HOR_TICK_POS_MAP[tick_pos]

    def reset_errors(self):
        """ Reset the error attributes of the component.

        """
        parent = self.parent
        parent.error = False
        parent.exception = None

    def notify(self, exception):
        """ Update the error attributes of the component.

        """
        parent = self.parent
        parent.error = True
        parent.exception = exception

