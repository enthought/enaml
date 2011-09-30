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

    #: Internal backup valid posistion value used to guard against errors
    #: with the from_slider and to_slider functions
    _backup = Float

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
        self._backup = parent.value
        self.set_value(parent.value)
        self.set_orientation(parent.orientation)
        self.set_tick_position(parent.tick_position)
        self.set_tick_frequency(parent.tick_interval)
        self.set_single_step(parent.single_step)
        self.set_page_step(parent.page_step)
        self.set_tracking(parent.tracking)

        self.bind()

    def parent_from_slider_changed(self, from_slider):
        """ Update the slider value with based on the new function

        Arguments
        ---------
        from_slider : Callable
            A function that takes one argument to convert from the slider
            position to the appropriate Python value.

        """
        parent = self.parent
        new_value = self.convert_position()
        parent.value = new_value

    def parent_to_slider_changed(self, to_slider):
        """ Update the slider position with based on the new function

        Arguments
        ---------
        to_slider : Callable
            A function that takes one argument to convert from a Python
            value to the appropriate slider position.

        """
        parent = self.parent
        position = self.validate(parent.value)
        self.set_in_widget(position)

    def parent_value_changed(self, value):
        """ Update the slider position value

        """
        self.set_value(value)


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

    def bind(self):
        """ Binds the event handlers for the slider widget.

        """
        widget = self.widget
        widget.valueChanged.connect(self._on_slider_changed)
        widget.sliderPressed.connect(self._on_pressed)
        widget.sliderReleased.connect(self._on_released)


    def _on_slider_changed(self, value):
        """ Respond to a (possible) change in value from the ui.

        """
        parent = self.parent
        new_value = self.convert_position()
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

    def set_value(self, value):
        """ Validate and set the slider widget position to the new value

        The assignment fail because `value` is out of range or the
        conversion through `to_slider` returns an exception. In that case
        the last known good value is given back to the parent.value
        attribute.

        """
        parent = self.parent

        position = self.validate(value, reset_errors = False)
        # the `value` and `position` variables will be different if the
        # validation failed.
        if value == position:
            self.set_in_widget(position)
            if position != self._backup:
                parent.moved = position
            self._backup = position
            self.reset_errors()
        else:
            exception = parent.exception
            parent.value = position
            parent.error = True
            parent.exception = exception

    def validate(self, value, reset_errors=True):
        """ Validate the position value.

        The method checks if the output of the :meth:`to_slider` function
        returns a value that can be converted to float and is in the range
        of [0.0, 1.0]. If the validation is not succesful it sets the
        `error` and `exception` attributes and returns the previous known
        good value.

        If the :attr:`reset_errors` is False then the method does not
        reset the error and exception attributes (unless there is an
        exception ofcourse)
        """
        parent = self.parent

        if reset_errors:
            self.reset_errors()

        try:
            position = float(parent.to_slider(parent.value))

            if not (0.0 <= position <= 1.0):
                raise ValueError('to_slider() must return a value '
                                            'between 0.0 and 1.0, but instead'
                                            ' returned %s'  % repr(position))
        except Exception as raised_exception:
            self.notify(raised_exception)
            position = self._backup

        return position

    def convert_position(self, reset_errors=True):
        """ Convert and return the slider position coming from the widget.

        The method checks if the :meth:`from_slider` function
        does not raise an exception. If the converison is not successful
        it sets the `error` and `exception` attributes and the current
        enaml component position.

        If the :attr:`reset_errors` is False then the method does not
        reset the error and exception attributes (unless there is an
        exception ofcourse).

        """
        parent = self.parent

        if reset_errors:
            self.reset_errors()

        value = self.retrieve_from_widget()

        try:
            position = parent.from_slider(value)
        except Exception as raised_exception:
            self.notify(raised_exception)
            position = parent.value

        return position

    def retrieve_from_widget(self):
        """ Get the slider position from the widget and convert to the
        enaml internal representation.

        """
        return self.widget.value() / float(SLIDER_MAX)


    def set_in_widget(self, value):
        """ set the slider position to the widget and convert to the
        enaml internal representation.

        """
        self.widget.setValue(value * SLIDER_MAX)

    def sync_tick_position(self):
        """ Syncornize the tick_position with the widget

        The QSlider automaticall updates or addaptes the tick position but
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

