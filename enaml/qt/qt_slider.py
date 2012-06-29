#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore
from .qt_constraints_widget import QtConstraintsWidget


#: A map from Enaml constants to QSlider TickPosition values.
_TICK_POSITION_MAP = {
    'no_ticks': QtGui.QSlider.NoTicks,
    'left': QtGui.QSlider.TicksLeft,
    'right': QtGui.QSlider.TicksRight,
    'top': QtGui.QSlider.TicksAbove,
    'bottom': QtGui.QSlider.TicksBelow,
    'both': QtGui.QSlider.TicksBothSides
}

#: A map from Enaml enums to Qt constants for horizontal or vertical 
#: orientation.
_ORIENTATION_MAP = {
    'horizontal': QtCore.Qt.Horizontal,
    'vertical': QtCore.Qt.Vertical
}


class QtSlider(QtConstraintsWidget):
    """ A Qt4 implementation of an Enaml Slider.

    """
    def create(self):
        """ Create the underlying QSlider widget.

        """
        self.widget = QtGui.QSlider(self.parent_widget)

    def initialize(self, init_attrs):
        """ Initialize the widget's attributes.

        """
        super(QtSlider, self).initialize(init_attrs)
        self.set_value(init_attrs.get('value', 0))
        self.set_maximum(init_attrs.get('maximum', 100))
        self.set_minimum(init_attrs.get('minimum', 0))
        self.set_orientation(init_attrs.get('orientation', 'horizontal'))
        self.set_page_step(init_attrs.get('page_step', 1))
        self.set_single_step(init_attrs.get('single_step', 1))
        self.set_tick_interval(init_attrs.get('tick_interval', 1))
        self.set_tick_position(init_attrs.get('tick_position', 'bottom'))
        self.set_tracking(init_attrs.get('tracking', True))

    def bind(self):
        """ Bind the signal handlers for the widget.

        """
        self.widget.valueChanged.connect(self.on_value_changed)
        self.widget.sliderMoved.connect(self.on_moved)
        self.widget.sliderPressed.connect(self.on_pressed)
        self.widget.sliderReleased.connect(self.on_released)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_value(self, ctxt):
        """ Handle the 'set_value' message from the Enaml widget.

        """
        return self.set_value(ctxt['value'])

    def receive_set_maximum(self, ctxt):
        """ Handle the 'set_maximum' message from the Enaml widget.

        """
        return self.set_maximum(ctxt['maximum'])

    def receive_set_minimum(self, ctxt):
        """ Handle the 'set_minimum' message from the Enaml widget.

        """
        return self.set_minimum(ctxt['minimum'])

    def receive_set_orientation(self, ctxt):
        """ Handle the 'set_orientation' message from the Enaml widget.

        """
        return self.set_orientation(ctxt['orientation'])

    def receive_set_page_step(self, ctxt):
        """ Handle the 'set_page_step' message from the Enaml widget.

        """
        return self.set_page_step(ctxt['page_step'])

    def receive_set_single_step(self, ctxt):
        """ Handle the 'set_single_step' message from the Enaml widget.

        """
        return self.set_single_step(ctxt['single_step'])

    def receive_set_tick_interval(self, ctxt):
        """ Handle the 'set_tick_interval' message from the Enaml widget.

        """
        return self.set_tick_interval(ctxt['tick_interval'])

    def receive_set_tick_position(self, ctxt):
        """ Handle the 'set_tick_position' message from the Enaml widget.

        """
        return self.set_tick_position(ctxt['tick_position'])

    def receive_set_tracking(self, ctxt):
        """ Handle the 'set_tracking' message from the Enaml widget.

        """
        return self.set_tracking(ctxt['tracking'])
    
    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_value_changed(self):
        """ Send the 'set_value' command to the Enaml widget when the 
        slider value has changed.

        """
        ctxt = {
            'action':'set_value',
            'value': self.widget.value()
        }
        self.send(ctxt)

    def on_moved(self):
        """ XXX

        """
        pass
    
    def on_pressed(self):
        """ XXX

        """
        pass

    def on_released(self):
        """ XXX

        """
        pass

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_value(self, value):
        """ Set the value of the underlying widget.

        """
        self.widget.setValue(value)
        return True

    def set_maximum(self, maximum):
        """ Set the maximum value of the underlying widget.

        """
        self.widget.setMaximum(maximum)
        return True

    def set_minimum(self, minimum):
        """ Set the minimum value of the underlying widget.

        """
        self.widget.setMinimum(minimum)
        return True

    def set_orientation(self, orientation):
        """ Set the orientation of the underlying widget.

        """
        self.widget.setOrientation(_ORIENTATION_MAP[orientation])
        return True

    def set_page_step(self, page_step):
        """ Set the page step of the underlying widget.

        """
        self.widget.setPageStep(page_step)
        return True

    def set_single_step(self, single_step):
        """ Set the single step of the underlying widget.

        """
        self.widget.setSingleStep(single_step)
        return True

    def set_tick_interval(self, tick_interval):
        """ Set the tick interval of the underlying widget

        """
        self.widget.setTickInterval(tick_interval)
        return True

    def set_tick_position(self, tick_position):
        """ Set the tick position of the underlying widget.

        """
        self.widget.setTickPosition(_TICK_POSITION_MAP[tick_position])
        return True

    def set_tracking(self, tracking):
        """ Set the tracking of the underlying widget.

        """
        self.widget.setTracking(tracking)
        return True
