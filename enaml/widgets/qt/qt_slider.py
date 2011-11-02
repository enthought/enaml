#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore
from .qt_control import QtControl
from ..slider import AbstractTkSlider

# A map from Enaml constants to QSlider TickPosition values.
TICK_POS_MAP = {'no_ticks': QtGui.QSlider.NoTicks,
                'left': QtGui.QSlider.TicksLeft,
                'right': QtGui.QSlider.TicksRight,
                'top': QtGui.QSlider.TicksAbove,
                'bottom': QtGui.QSlider.TicksBelow,
                'both': QtGui.QSlider.TicksBothSides}

# A map from Enaml enums to Qt constants for horizontal or vertical orientation.
ORIENTATION_MAP = {'horizontal': QtCore.Qt.Horizontal,
                   'vertical': QtCore.Qt.Vertical}


# Qt Slider does not return TicksLeft and TicksRight it always
# converts these to TicksAbove and TicksBelow so we need to check
# the orientation in order to return the right result

# A map from horizontal QSlider TickPosition values to Enaml constants.
HOR_TICK_POS_MAP = {QtGui.QSlider.NoTicks: 'no_ticks',
                    QtGui.QSlider.TicksAbove: 'top',
                    QtGui.QSlider.TicksBelow: 'bottom',
                    QtGui.QSlider.TicksBothSides: 'both'}

# A map from vertical QSlider TickPosition values to Enaml constants.
VERT_TICK_POS_MAP = {QtGui.QSlider.NoTicks: 'no_ticks',
                    QtGui.QSlider.TicksAbove: 'left',
                    QtGui.QSlider.TicksBelow: 'right',
                    QtGui.QSlider.TicksBothSides: 'both'}


class QtSlider(QtControl, AbstractTkSlider):
    """ A Qt implementation of Slider.

    See Also
    --------
    Slider

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QSlider widget.

        """
        self.widget = QtGui.QSlider(parent=self.parent_widget())

    def initialize(self):
        """ Initializes the attributes of the toolkit widget.

        """
        super(QtSlider, self).initialize()
        shell = self.shell_obj
        shell._down = False

        self.set_range(shell.minimum, shell.maximum)
        self.set_position(shell.value)
        self.set_orientation(shell.orientation)
        self.set_tick_position(shell.tick_position)
        self.set_tick_frequency(shell.tick_interval)
        self.set_single_step(shell.single_step)
        self.set_page_step(shell.page_step)
        self.set_tracking(shell.tracking)

    def bind(self):
        """ connect the event handlers for the slider widget signals.

        """
        super(QtSlider, self).bind()
        widget = self.widget
        widget.valueChanged.connect(self._on_slider_changed)
        widget.sliderPressed.connect(self._on_pressed)
        widget.sliderReleased.connect(self._on_released)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell__minimum_changed(self, minimum):
        """ Update the slider when the converter class changes.

        """
        shell = self.shell_obj
        self.set_range(minimum, shell.maximum)

    def shell__maximum_changed(self, maximum):
        """ Update the slider when the converter class changes.

        """
        shell = self.shell_obj
        self.set_range(shell.minimum, maximum)

    def shell_value_changed(self, value):
        """ Update the slider position

        """
        self.set_position(value)
        self.shell_obj.moved = value

    def shell_tracking_changed(self, tracking):
        """ Set the tracking event in the widget

        """
        self.set_tracking(tracking)

    def shell_single_step_changed(self, single_step):
        """ Update the the line step in the widget.

        """
        self.set_single_step(single_step)

    def shell_page_step_changed(self, page_step):
        """ Update the widget due to change in the line step.

        """
        self.set_page_step(page_step)

    def shell_tick_interval_changed(self, tick_interval):
        """ Update the tick marks interval.

        """
        shell = self.shell
        self.set_tick_frequency(tick_interval)
        self.set_single_step(shell.single_step)
        self.set_page_step(shell.page_step)

    def shell_tick_position_changed(self, tick_position):
        """ Update the widget due to change in the tick position

        The method ensures that the tick position style can be applied
        and reverts to the last value if the request is invalid.

        """
        self.set_tick_position(tick_position)

    def shell_orientation_changed(self, orientation):
        """ Update the widget due to change in the orientation attribute

        The method applies the orientation style and fixes the tick position
        option if necessary.

        """
        self.set_orientation(orientation)

    def _on_slider_changed(self, value):
        """ Respond to a change in value of the slider widget.

        """
        shell = self.shell_obj
        new_value = self.get_position()
        shell.value = new_value

    def _on_pressed(self):
        """ Update if the left button was pressed.

        Estimates the position of the thumb and then checks if the mouse
        was pressed over it to fire the `pressed` event and sets the
        `down` attribute.

        """
        shell = self.shell_obj
        shell._down = True
        shell.pressed = True

    def _on_released(self):
        """ Update if the left button was released

        Checks if the `down` attribute was set. In that case the
        function fires the release event and sets the `down` attribute to
        false.

        """
        shell = self.shell_obj
        if shell._down:
            shell._down = False
            shell.released = True

    def set_single_step(self, step):
        """ Set the single step attribute in the Qt widget.

        Arguments
        ---------
        step: int
            the number of steps (in tick intervals) to move the slider
            when the user uses the arrow keys.

        """
        widget = self.widget
        widget.setSingleStep(step)

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
        widget.setPageStep(step)

    def set_tick_position(self, ticks):
        """ Apply the tick position in the widget.

        The tick_position is addapted to reflect the current orientation.
        This is agrees with how the QSlider is behaving.

        Arguments
        ---------
        ticks : str
            The :class:`~enaml.enums.TickPosition` value.
        """
        constant = TICK_POS_MAP[ticks]
        self.widget.setTickPosition(constant)
        self.sync_tick_position()

    def set_orientation(self, orientation):
        """ Set the slider orientation

        Arguments
        ---------
        orientation : str
            The orientation of the slider, ``vertical`` or ``horizontal``.

        """
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
        self.widget.setTickInterval(interval)

    def set_position(self, value):
        """ Validate the position value.

        """
        self.widget.setValue(value)
    def get_position(self):
        """ Get the slider position from the widget.

        """
        return self.widget.value()

    def sync_tick_position(self):
        """ Syncornize the tick_position with the widget

        The QSlider automatically updates or adaptes the tick position but
        we still need to update the enaml component, so that it is in sync.

        """
        shell = self.shell_obj
        orientation = shell.orientation
        tick_pos = self.widget.tickPosition()
        if orientation == 'vertical':
            shell.tick_position = VERT_TICK_POS_MAP[tick_pos]
        else:
            shell.tick_position = HOR_TICK_POS_MAP[tick_pos]
