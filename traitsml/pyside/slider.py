from enthought.traits.api import Bool, DelegatesTo, ReadOnly

from PySide import QtCore, QtGui

from ..constants import Orientation, TickPosition
from .element import Element
from .mixins import GeneralWidgetMixin


ORIENTATION_MAP = {Orientation.DEFAULT: QtCore.Qt.Vertical,
                   Orientation.HORIZONTAL: QtCore.Qt.Horizontal,
                   Orientation.VERTICAL: QtCore.Qt.Vertical}


TICK_POS_MAP = {TickPosition.DEFAULT: QtGui.QSlider.NoTicks,
                TickPosition.NO_TICKS: QtGui.QSlider.NoTicks,
                TickPosition.BOTH_SIDES: QtGui.QSlider.TicksBothSides,
                TickPosition.ABOVE: QtGui.QSlider.TicksAbove,
                TickPosition.BELOW: QtGui.QSlider.TicksBelow,
                TickPosition.LEFT: QtGui.QSlider.TicksLeft,
                TickPosition.RIGHT: QtGui.QSlider.TicksRight}



class SliderWidget(GeneralWidgetMixin, QtGui.QSlider):
    pass


class Slider(Element):

    # A slider's range is fixed at 0.0 to 1.0. Therefore, the 
    # position of the slider can be viewed as a percentage. 
    # To facilitate various ranges, you can specify from_pos
    # and to_pos callables to convert to and from the position
    # the value. By default, these callables are just pass through.

    # Whether or not the slider is pressed down - Bool
    down = DelegatesTo('abstract_obj')
    
    # The conversion function to convert from slider_pos to value. - Callable
    from_slider = DelegatesTo('abstract_obj')
    
    # The multi tick step for paging - Float
    multi_step = DelegatesTo('abstract_obj')
    
    # A flag to prevent infinite recursion when updating the widget.
    no_update = Bool(False)

    # The orientation of the slider - Enum of Orientation values
    orientation = DelegatesTo('abstract_obj')
    
    # The floating point percentage (0.0 - 1.0) which is 
    # the position of the slider. Always updated while sliding. - Float
    slider_pos = DelegatesTo('abstract_obj')
    
    # The minimum integer value for the QSlider.
    q_slider_min = ReadOnly(0)

    # The maximum integer value for the QSlider
    q_slider_max = ReadOnly(10000)

    # The single tick step for the slider for arrow presses - Float
    single_step = DelegatesTo('abstract_obj')

    # The interval (value interval, not pixel interval) to put
    # between tick marks. The default is zero and indicates that
    # the toolkit can choose between single_step and multi_step. - Float
    tick_interval = DelegatesTo('abstract_obj')

    # Where to draw the ticks marks for the slider - Enum of TickPosition
    tick_pos = DelegatesTo('abstract_obj')
    
    # The conversion function to convert from value to slider_pos. - Callable
    to_slider = DelegatesTo('abstract_obj')

    # Whether or not the value should be updated when sliding,
    # or only when the slider is released - Bool
    tracking = DelegatesTo('abstract_obj')

    # The value of the slider. Will be set to from_pos(slider_pos).
    # Changes to this value will update the position and vice-versa. - Any
    value = DelegatesTo('abstract_obj')
    
    #--------------------------------------------------------------------------
    # Creation Handler
    #--------------------------------------------------------------------------
    def create_widget(self):
        return SliderWidget()

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def init_widget(self):
        super(Slider, self).init_widget()
        widget = self.widget
        widget.sliderMoved.connect(self._on_slider_moved)
        widget.sliderPressed.connect(self._on_slider_pressed)
        widget.sliderReleased.connect(self._on_slider_released)
        widget.valueChanged.connect(self._on_value_changed)
    
    def init_attributes(self):
        super(Slider, self).init_attributes()
        self.init_max()
        self.init_min()
        self.init_down()
        self.init_orientation()
        self.init_single_step()
        self.init_multi_step()
        self.init_tick_interval()
        self.init_tick_pos()
        self.init_tracking()
        self.init_slider_pos()
    
    def init_max(self):
        self.widget.setMaximum(self.q_slider_max)

    def init_min(self):
        self.widget.setMinimum(self.q_slider_min)

    def init_down(self):
        self.widget.setSliderDown(self.down)

    def init_orientation(self):
        q_orientation = ORIENTATION_MAP[self.orientation]
        self.widget.setOrientation(q_orientation)
            
    def init_single_step(self):
        step = self._single_step()
        self.widget.setSingleStep(step)

    def init_multi_step(self):
        step = self._multi_step()
        self.widget.setPageStep(step)

    def init_tick_interval(self):
        interval = self._tick_interval()
        self.widget.setTickInterval(interval)

    def init_tick_pos(self):
        q_tick_pos = TICK_POS_MAP[self.tick_pos]
        self.widget.setTickPosition(q_tick_pos)

    def init_tracking(self):
        self.widget.setTracking(self.tracking)

    def init_slider_pos(self):
        self.slider_pos = self._slider_pos_from_value()
    
    #--------------------------------------------------------------------------
    # Change handlers
    #--------------------------------------------------------------------------
    def _down_changed(self):
        self.widget.setSliderDown(self.down)

    def _from_slider_changed(self):
        self.value = self._value_from_slider_pos()

    def _multi_step_changed(self):
        step = self._multi_step()
        self.widget.setPageStep(step)

    def _orientation_changed(self):
        q_orientation = ORIENTATION_MAP[self.orientation]
        self.widget.setOrientation(q_orientation)

    def _slider_pos_changed(self):
        if not self.no_update:
            self.no_update = True
            slider = self._slider_from_slider_pos()
            self.widget.setSliderPosition(slider)
            self.value = self._value_from_slider_pos()
            self.no_update = False

    def _single_step_changed(self):
        step = self._single_step()
        self.widget.setSingleStep(step)

    def _tick_interval_changed(self):
        interval = self._tick_interval()
        self.widget.setTickInterval(interval)

    def _tick_pos_changed(self):
        q_tick_pos = TICK_POS_MAP[self.tick_pos]
        self.widget.setTickPosition(q_tick_pos)

    def _to_slider_changed(self):
        self.slider_pos = self._slider_pos_from_value()

    def _tracking_changed(self):
        self.widget.setTracking(self.tracking)

    def _value_changed(self):
        self.slider_pos = self._slider_pos_from_value() 

    #--------------------------------------------------------------------------
    # Slots
    #--------------------------------------------------------------------------
    def _on_slider_moved(self):
        self.slider_pos = self._slider_pos_from_slider()
        
    def _on_slider_pressed(self):
        self.down = self.widget.isSliderDown()

    def _on_slider_released(self):
        self.down = self.widget.isSliderDown()

    def _on_value_changed(self):
        self.slider_pos = self._slider_pos_from_slider()

    #--------------------------------------------------------------------------
    # Computation Methods
    #--------------------------------------------------------------------------
    def _single_step(self):
        span = self.q_slider_max - self.q_slider_min
        step = self.single_step * span
        return int(step)

    def _multi_step(self):
        span = self.q_slider_max - self.q_slider_min
        step = self.multi_step * span
        return int(step)
    
    def _tick_interval(self):
        span = self.q_slider_max - self.q_slider_min
        interval = self.tick_interval * span
        return int(interval)

    def _slider_pos_from_value(self):
        return self.to_slider(self.value)

    def _value_from_slider_pos(self):
        return self.from_slider(self.slider_pos)

    def _slider_pos_from_slider(self):
        slider_pos = self.widget.sliderPosition()
        span = float(self.q_slider_max - self.q_slider_min)
        return slider_pos / span
    
    def _slider_from_slider_pos(self):
        pos = self.slider_pos
        span = float(self.q_slider_max - self.q_slider_min)
        return int(pos * span)


