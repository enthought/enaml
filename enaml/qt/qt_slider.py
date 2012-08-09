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

    def initialize(self, attrs):
        """ Initialize the widget's attributes.

        """
        super(QtSlider, self).initialize(attrs)
        self.set_value(attrs['value'])
        self.set_maximum(attrs['maximum'])
        self.set_minimum(attrs['minimum'])
        self.set_orientation(attrs['orientation'])
        self.set_page_step(attrs['page_step'])
        self.set_single_step(attrs['single_step'])
        self.set_tick_interval(attrs['tick_interval'])
        self.set_tick_position(attrs['tick_position'])
        self.set_tracking(attrs['tracking'])
        self.widget.valueChanged.connect(self.on_value_changed)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_value(self, content):
        """ Handle the 'set_value' action from the Enaml widget.

        """
        self.set_value(content['value'])

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

    def on_action_set_page_step(self, content):
        """ Handle the 'set_page_step' action from the Enaml widget.

        """
        self.set_page_step(content['page_step'])

    def on_action_set_single_step(self, content):
        """ Handle the 'set_single_step' action from the Enaml widget.

        """
        self.set_single_step(content['single_step'])

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
    def on_value_changed(self):
        """ Send the 'value_changed' action to the Enaml widget when the 
        slider value has changed.

        """
        content = {'value': self.widget.value()}
        self.send_action('value_changed', content)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_value(self, value):
        """ Set the value of the underlying widget.

        """
        self.widget.setValue(value)

    def set_maximum(self, maximum):
        """ Set the maximum value of the underlying widget.

        """
        self.widget.setMaximum(maximum)

    def set_minimum(self, minimum):
        """ Set the minimum value of the underlying widget.

        """
        self.widget.setMinimum(minimum)

    def set_orientation(self, orientation):
        """ Set the orientation of the underlying widget.

        """
        self.widget.setOrientation(_ORIENTATION_MAP[orientation])

    def set_page_step(self, page_step):
        """ Set the page step of the underlying widget.

        """
        self.widget.setPageStep(page_step)

    def set_single_step(self, single_step):
        """ Set the single step of the underlying widget.

        """
        self.widget.setSingleStep(single_step)

    def set_tick_interval(self, interval):
        """ Set the tick interval of the underlying widget.

        """
        self.widget.setTickInterval(interval)

    def set_tick_position(self, tick_position):
        """ Set the tick position of the underlying widget.

        """
        self.widget.setTickPosition(_TICK_POSITION_MAP[tick_position])

    def set_tracking(self, tracking):
        """ Set the tracking of the underlying widget.

        """
        self.widget.setTracking(tracking)

