#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt, Signal
from .qt.QtGui import (
    QSlider, QStyle, QStyleOptionSlider, QPainter,
    )
from .qt_control import QtControl


#: A map from Enaml constants to QSlider TickPosition values.
_TICK_POSITION_MAP = {
    'no_ticks': QSlider.NoTicks,
    'left': QSlider.TicksLeft,
    'right': QSlider.TicksRight,
    'top': QSlider.TicksAbove,
    'bottom': QSlider.TicksBelow,
    'both':QSlider.TicksBothSides
}


#: A map from Enaml enums to Qt constants for horizontal or vertical
#: orientation.
_ORIENTATION_MAP = {
    'horizontal': Qt.Horizontal,
    'vertical': Qt.Vertical
}


class QDualSlider(QSlider):
    """ A Qt implementation of a dual slider.

        This class provides a dual-slider for ranges, where there is a defined
        maximum and minimum, as is a normal slider, but instead of having a
        single slider value, there are 2 slider values.

    """

    lowValueChanged = Signal(int)

    highValueChanged = Signal(int)

    def __init__(self, *args):
        super(QDualSlider, self).__init__(*args)

        self._low = self.minimum()
        self._high = self.maximum()

        self._pressed_control = QStyle.SC_None
        self._hover_control = QStyle.SC_None
        self._click_offset = 0

        # 0 for the low, 1 for the high, -1 for both
        self._active_slider = 0

    def lowValue(self):
        return self._low

    def setLowValue(self, low):
        self._low = low
        self.update()

    def highValue(self):
        return self._high

    def setHighValue(self, high):
        self._high = high
        self.update()

    def paintEvent(self, event):
        # based on http://qt.gitorious.org/qt/qt/blobs/master/src/gui/widgets/qslider.cpp

        painter = QPainter(self)
        style = self.style()

        for i, value in enumerate([self._low, self._high]):
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)

            # Only draw the groove for the first slider so it doesn't get drawn
            # on top of the existing ones every time
            if i == 0:
                opt.subControls = QStyle.SC_SliderGroove | QStyle.SC_SliderHandle
            else:
                opt.subControls = QStyle.SC_SliderHandle

            if self.tickPosition() != self.NoTicks:
                opt.subControls |= QStyle.SC_SliderTickmarks

            if self._pressed_control and self._active_slider == i:
                opt.activeSubControls = self._pressed_control
                opt.state |= QStyle.State_Sunken
            else:
                opt.activeSubControls = self._hover_control

            opt.sliderPosition = value
            opt.sliderValue = value
            style.drawComplexControl(QStyle.CC_Slider, opt, painter, self)

    def mousePressEvent(self, event):
        event.accept()

        style = self.style()
        button = event.button()

        # In a normal slider control, when the user clicks on a point in the
        # slider's total range, but not on the slider part of the control the
        # control would jump the slider value to where the user clicked.
        # For this control, clicks which are not direct hits will slide both
        # slider parts

        if button:
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)

            self._active_slider = -1

            for i, value in enumerate([self._low, self._high]):
                opt.sliderPosition = value
                hit = style.hitTestComplexControl(style.CC_Slider, opt, event.pos(), self)
                if hit == style.SC_SliderHandle:
                    self._active_slider = i
                    self._pressed_control = hit

                    self.triggerAction(self.SliderMove)
                    self.setRepeatAction(self.SliderNoAction)
                    self.setSliderDown(True)
                    break

            if self._active_slider < 0:
                self._pressed_control = QStyle.SC_SliderHandle
                self._click_offset = self._pixelPosToRangeValue(self._pick(event.pos()), opt)
                self.triggerAction(self.SliderMove)
                self.setRepeatAction(self.SliderNoAction)
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self._pressed_control != QStyle.SC_SliderHandle:
            event.ignore()
            return

        event.accept()
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        new_pos = self._pixelPosToRangeValue(self._pick(event.pos()), opt)

        if self._active_slider < 0:
            offset = new_pos - self._click_offset
            self._high += offset
            self._low += offset
            if self._low < self.minimum():
                diff = self.minimum() - self._low
                self._low += diff
                self._high += diff
            if self._high > self.maximum():
                diff = self.maximum() - self._high
                self._low += diff
                self._high += diff
        elif self._active_slider == 0:
            if new_pos >= self._high:
                new_pos = self._high - 1
            self._low = new_pos
        else:
            if new_pos <= self._low:
                new_pos = self._low + 1
            self._high = new_pos

        self._click_offset = new_pos

        self.update()

        if self._active_slider != 1:
            self.lowValueChanged.emit(new_pos)
        if self._active_slider != 0:
            self.highValueChanged.emit(new_pos)

    def mouseReleaseEvent(self, event):
        if self._pressed_control == QStyle.SC_None:
            event.ignore()
            return

        event.accept()
        if self._pressed_control == QStyle.SC_SliderHandle:
            self.setSliderDown(False)
        self._pressed_control = QStyle.SC_None
        self.setRepeatAction(self.SliderNoAction)
        self.update()

    def _pick(self, pt):
        if self.orientation() == Qt.Horizontal:
            return pt.x()
        else:
            return pt.y()

    def _pixelPosToRangeValue(self, pos, opt):

        style = self.style()

        gr = style.subControlRect(style.CC_Slider, opt, style.SC_SliderGroove, self)
        sr = style.subControlRect(style.CC_Slider, opt, style.SC_SliderHandle, self)

        if self.orientation() == Qt.Horizontal:
            slider_length = sr.width()
            slider_min = gr.x()
            slider_max = gr.right() - slider_length + 1
        else:
            slider_length = sr.height()
            slider_min = gr.y()
            slider_max = gr.bottom() - slider_length + 1

        return style.sliderValueFromPosition(self.minimum(), self.maximum(),
                                             pos-slider_min, slider_max-slider_min,
                                             opt.upsideDown)


class QtDualSlider(QtControl):
    """ A Qt implementation of an Enaml Slider.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QSlider widget.

        """
        return QDualSlider(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtDualSlider, self).create(tree)
        # Initialize the value after the minimum and maximum to avoid
        # the potential for premature internal clipping of the value.
        self.set_minimum(tree['minimum'])
        self.set_maximum(tree['maximum'])
        self.set_low_value(tree['low_value'])
        self.set_high_value(tree['high_value'])
        self.set_orientation(tree['orientation'])
        self.set_tick_interval(tree['tick_interval'])
        self.set_tick_position(tree['tick_position'])
        self.set_tracking(tree['tracking'])
        self.widget().lowValueChanged.connect(self.on_low_value_changed)
        self.widget().highValueChanged.connect(self.on_high_value_changed)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_low_value(self, content):
        """ Handle the 'set_low_value' action from the Enaml widget.

        """
        self.set_low_value(content['low_value'])

    def on_action_set_high_value(self, content):
        """ Handle the 'set_high_value' action from the Enaml widget.

        """
        self.set_high_value(content['high_value'])

    def on_action_set_maximum(self, content):
        """ Handle the 'set_maximum' action from the Enaml widget.

        """
        self.set_maximum(content['maximum'])

    def on_action_set_minimum(self, content):
        """ Handle the 'set_minimum' action from the Enaml widget.

        """
        self.set_minimum(content['minimum'])

    def on_action_set_orientation(self, content):
        """ Handle the 'set_orientation' action from the Enaml widget.

        """
        self.set_orientation(content['orientation'])

    def on_action_set_tick_interval(self, content):
        """ Handle the 'set_tick_interval' action from the Enaml widget.

        """
        self.set_tick_interval(content['tick_interval'])

    def on_action_set_tick_position(self, content):
        """ Handle the 'set_tick_position' action from the Enaml widget.

        """
        self.set_tick_position(content['tick_position'])

    def on_action_set_tracking(self, content):
        """ Handle the 'set_tracking' action from the Enaml widget.

        """
        self.set_tracking(content['tracking'])

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_high_value_changed(self):
        """ Send the 'value_changed' action to the Enaml widget when the
        slider value has changed.

        """
        if 'high_value' not in self.loopback_guard:
            content = {'high_value': self.widget().highValue()}
            self.send_action('high_value_changed', content)

    def on_low_value_changed(self):
        """ Send the 'low_value_changed' action to the Enaml widget when the
        slider value has changed.

        """
        if 'low_value' not in self.loopback_guard:
            content = {'low_value': self.widget().lowValue()}
            self.send_action('low_value_changed', content)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_low_value(self, value):
        """ Set the low value of the underlying widget.

        """
        with self.loopback_guard('low_value'):
            self.widget().setLowValue(value)

    def set_high_value(self, value):
        """ Set the high value of the underlying widget.

        """
        with self.loopback_guard('high_value'):
            self.widget().setHighValue(value)

    def set_maximum(self, maximum):
        """ Set the maximum value of the underlying widget.

        """
        self.widget().setMaximum(maximum)

    def set_minimum(self, minimum):
        """ Set the minimum value of the underlying widget.

        """
        self.widget().setMinimum(minimum)

    def set_orientation(self, orientation):
        """ Set the orientation of the underlying widget.

        """
        self.widget().setOrientation(_ORIENTATION_MAP[orientation])

    def set_tick_interval(self, interval):
        """ Set the tick interval of the underlying widget.

        """
        self.widget().setTickInterval(interval)

    def set_tick_position(self, tick_position):
        """ Set the tick position of the underlying widget.

        """
        self.widget().setTickPosition(_TICK_POSITION_MAP[tick_position])

    def set_tracking(self, tracking):
        """ Set the tracking of the underlying widget.

        """
        self.widget().setTracking(tracking)

