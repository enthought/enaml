from .qt import QtGui, QtCore

from traits.api import implements, Bool, TraitError

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
ORIENTATION_MAP = {Orientation.DEFAULT: QtCore.Qt.Vertical,
                   Orientation.HORIZONTAL: QtCore.Qt.Horizontal,
                   Orientation.VERTICAL: QtCore.Qt.Vertical}


class QtSlider(QtControl):
    """ A Qt implementation of Slider.

    See Also
    --------
    Slider

    """
    implements(ISliderImpl)

    #: When set to True, the enaml widget is still initialising.
    #: It is mainly used to control the event firing behaviour
    #: of the widget during initialisation
    _initialising = Bool

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
        self._initialising = True

        parent = self.parent
        parent._down = False
        parent.slider_pos = parent.to_slider(parent.value)

        # We hard-coded range for the widget since we are managing the
        # conversion.
        self.set_range(0, SLIDER_MAX)
        self.set_position(parent.slider_pos)
        self.set_orientation(parent.orientation)
        self.set_tick_position(parent.tick_position)
        self.set_tick_frequency(parent.tick_interval)
        self.set_single_step(parent.single_step)
        self.set_page_step(parent.page_step)
        self.set_tracking(parent.tracking)

        self.bind()

        self._initialising = False

    def parent_from_slider_changed(self, from_slider):
        """ Update the slider value with based on the new function

        Arguments
        ---------
        from_slider : Callable
            A function that takes one argument to convert from the slider
            postion to the appropriate Python value.

        """
        parent = self.parent
        parent.value = from_slider(parent.slider_pos)

    def parent_to_slider_changed(self, to_slider):
        """ Update the slider position with based on the new function

        Arguments
        ---------
        to_slider : Callable
            A function that takes one argument to convert from a Python
            value to the appropriate slider position.
        """
        parent = self.parent
        parent.slider_pos = to_slider(parent.value)

    def parent_slider_pos_changed(self, slider_pos):
        """ Update the position in the slider widget

        """
        parent = self.parent
        self.set_position(slider_pos)
        parent.value = value = parent.from_slider(slider_pos)

        # The move event is not fired during initialisation
        if not self._initialising:
            parent.moved = value

    def parent_value_changed(self, value):
        """ Update the slider position value

        Update the `slider_pos` to respond to the `value` change. The
        assignment to the slider_pos might fail because `value` is out
        of range. In that case the last known good value is given back
        to the value attribute.

        """
        parent = self.parent

        # The try...except block is required because we need to keep the
        # `value` attribute in sync with the `slider_pos` and **valid**
        try:
            parent.slider_pos = parent.to_slider(value)
        except TraitError as error:
            # revert value
            parent.value = parent.from_slider(parent.slider_pos)
            parent.invalid_value = error

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

        Individual event binding was preferred instead of events that
        are platform specific (e.g. wx.EVT_SCROLL_CHANGED) or group
        events (e.g. wx.EVT_SCROLL), to facilitate finer control on
        the behaviour of the widget.

        """
        widget = self.widget
        widget.valueChanged.connect(self._on_slider_changed)
        widget.sliderPressed.connect(self._on_pressed)
        widget.sliderReleased.connect(self._on_released)
    

    def _on_slider_changed(self, value):
        """ Respond to a (possible) change in value from the ui.

        Updated the value of the slider_pos based on the possible change
        from the wxWidget. The `slider_pos` trait will fire the moved
        event only if the value has changed.

        """
        self.parent.slider_pos = self.get_position()

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
        function calls the `_on_slider_changed` function, fires the
        release event and sets the `down` attribute to false.

        """
        parent = self.parent
        ##self._on_slider_changed(event)
        parent._down = False
        parent.released = True

    def set_single_step(self, step):
        """ Set the single step attribute in the wx widget.

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
        """ Set the page step attribute in the wx widget.

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

    def set_position(self, value):
        """Set the slider position to value.

        Converts the 'value' to an integer and changes the position of
        the slider in the widget if necessary.

        Arguments
        ---------
        value : float
            The new position of the slider in the range 0.0 - 1.0.

        """
        position = value * SLIDER_MAX
        if position != self.widget.value():
            self.widget.setValue(position)

    def get_position(self):
        """Get the slider position.

        Read the slider position from the widget and convert it to a
        float.

        Returns
        -------
        value : float
            The position of the widget slider in the range 0.0 - 1.0.

        """
        wx_position = float(self.widget.value())
        return wx_position / SLIDER_MAX

    def set_tick_position(self, ticks):
        """ Apply the tick position in the widget.

        Arguments
        ---------
        ticks : TickPosition
            The tick position

        Returns
        -------
        result : boolean
            True if the new value was valid. False if the value is
            invalid.

        """
        constant = TICK_POS_MAP[ticks]
        self.widget.setTickPosition(constant)

    def set_orientation(self, orientation):
        """ Set the slider orientation

        Arguments
        ---------
        orientation : Orientation
            The orientation of the slider.

        """
        constant = ORIENTATION_MAP[orientation]
        self.widget.setOrientation(constant)

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
