#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore
from .qt_control import QtControl

from ..slider import AbstractTkSlider


#: A map from Enaml constants to QSlider TickPosition values.
TICK_POS_MAP = {'no_ticks': QtGui.QSlider.NoTicks,
                'left': QtGui.QSlider.TicksLeft,
                'right': QtGui.QSlider.TicksRight,
                'top': QtGui.QSlider.TicksAbove,
                'bottom': QtGui.QSlider.TicksBelow,
                'both': QtGui.QSlider.TicksBothSides}


#: A map from Enaml enums to Qt constants for horizontal or vertical 
#: orientation.
ORIENTATION_MAP = {'horizontal': QtCore.Qt.Horizontal,
                   'vertical': QtCore.Qt.Vertical}


# Qt Slider does not return TicksLeft and TicksRight it always
# converts these to TicksAbove and TicksBelow so we need to check
# the orientation in order to return the right result

#: A map from horizontal QSlider TickPosition values to Enaml 
#: constants.
HOR_TICK_POS_MAP = {QtGui.QSlider.NoTicks: 'no_ticks',
                    QtGui.QSlider.TicksAbove: 'top',
                    QtGui.QSlider.TicksBelow: 'bottom',
                    QtGui.QSlider.TicksBothSides: 'both'}


#: A map from vertical QSlider TickPosition values to Enaml 
#: constants.
VERT_TICK_POS_MAP = {QtGui.QSlider.NoTicks: 'no_ticks',
                    QtGui.QSlider.TicksAbove: 'left',
                    QtGui.QSlider.TicksBelow: 'right',
                    QtGui.QSlider.TicksBothSides: 'both'}


class QtSlider(QtControl, AbstractTkSlider):
    """ A Qt implementation of Slider.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QSlider widget.

        """
        self.widget = QtGui.QSlider(parent=parent)

    def initialize(self):
        """ Initializes the attributes of the toolkit widget.

        """
        super(QtSlider, self).initialize()
        shell = self.shell_obj
        shell._down = False
        self.set_range(shell.minimum, shell.maximum)
        self.set_position(shell.value)
        self.set_tick_position(shell.tick_position)
        self.set_orientation(shell.orientation)
        self.set_tick_frequency(shell.tick_interval)
        self.set_single_step(shell.single_step)
        self.set_page_step(shell.page_step)
        self.set_tracking(shell.tracking)

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
    def shell_minimum_changed(self, minimum):
        """ The change handler for the 'minimum' attribute on the shell
        object.

        """
        self.set_range(minimum, self.shell_obj.maximum)

    def shell_maximum_changed(self, maximum):
        """ The change handler for the 'maximum' attribute on the shell
        object.
        
        """
        self.set_range(self.shell_obj.minimum, maximum)

    def shell_value_changed(self, value):
        """ The change handler for the 'value' attribute on the shell
        object.
        
        """
        self.set_position(value)

    def shell_tracking_changed(self, tracking):
        """ The change handler for the 'tracking' attribute on the shell
        object.

        """
        self.set_tracking(tracking)

    def shell_single_step_changed(self, single_step):
        """ The change handler for the 'single_step' attribute on the 
        shell object.
        
        """
        self.set_single_step(single_step)

    def shell_page_step_changed(self, page_step):
        """ The change handler for the 'page_step' attribute on the 
        shell object.

        """
        self.set_page_step(page_step)

    def shell_tick_interval_changed(self, tick_interval):
        """ The change handler for the 'tick_interval' attribute on the
        shell object.

        """
        shell = self.shell
        self.set_tick_frequency(tick_interval)
        # This extra calls are made since the range trait on 
        # shell object may clip the values to fit within the 
        # range without firing a changed notification.
        self.set_single_step(shell.single_step)
        self.set_page_step(shell.page_step)

    def shell_tick_position_changed(self, tick_position):
        """ The change handler for the 'tick_position' attribute on the
        shell object.

        """
        self.set_tick_position(tick_position)
        self.shell_obj.size_hint_updated()
        
    def shell_orientation_changed(self, orientation):
        """ The change handler for the 'orientation' attribute on the 
        shell object.

        """
        self.set_orientation(orientation)
        self.shell_obj.size_hint_updated()

    #--------------------------------------------------------------------------
    # Event Handlers 
    #--------------------------------------------------------------------------
    def _on_slider_changed(self):
        """ The event handler for the slider value changed event.

        """
        self.shell_obj.value = self.widget.value()

    def _on_slider_moved(self):
        """ The event handler for a slider moved event.

        """
        self.shell_obj.moved(self.widget.sliderPosition())

    def _on_pressed(self):
        """ Update if the left button was pressed.

        Estimates the position of the thumb and then checks if the mouse
        was pressed over it to fire the `pressed` event and sets the
        `down` attribute.

        """
        shell = self.shell_obj
        shell._down = True
        shell.pressed()

    def _on_released(self):
        """ Update if the left button was released

        Checks if the `down` attribute was set. In that case the
        function fires the release event and sets the `down` attribute to
        false.

        """
        shell = self.shell_obj
        if shell._down:
            shell._down = False
            shell.released()

    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_single_step(self, step):
        """ Set the single step attribute in the Qt widget.

        """
        self.widget.setSingleStep(step)

    def set_page_step(self, step):
        """ Set the page step attribute in the Qt widget.

        """
        self.widget.setPageStep(step)

    def set_tick_position(self, ticks):
        """ Apply the tick position in the widget.

        """
        self.widget.setTickPosition(TICK_POS_MAP[ticks])
        self.sync_tick_position()

    def set_orientation(self, orientation):
        """ Set the slider orientation.

        """
        self.widget.setOrientation(ORIENTATION_MAP[orientation])
        self.sync_tick_position()

    def set_tracking(self, tracking):
        """ Set the tracking state of the slider.

        """
        self.widget.setTracking(tracking)

    def set_range(self, minimum, maximum):
        """ Set the range of the slider widget.

        """
        self.widget.setRange(minimum, maximum)

    def set_tick_frequency(self, interval):
        """ Set the slider widget tick mark fequency.

        """
        self.widget.setTickInterval(interval)

    def set_position(self, value):
        """ Validate the position value.

        """
        self.widget.setValue(value)

    def sync_tick_position(self):
        """ Syncornize the tick_position with the widget. The QSlider 
        automatically updates or adaptes the tick position but we still 
        need to update the enaml component, so that it is in sync.

        """
        shell = self.shell_obj
        orientation = shell.orientation
        tick_pos = self.widget.tickPosition()
        if orientation == 'vertical':
            shell.tick_position = VERT_TICK_POS_MAP[tick_pos]
        else:
            shell.tick_position = HOR_TICK_POS_MAP[tick_pos]

