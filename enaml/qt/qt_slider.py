#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QSlider
from .qt_widget_component import QtWidgetComponent


class QtSlider(QtWidgetComponent):
    """ A Qt4 implementation of an Enaml Slider.

    """
    def create(self):
        """ Create the underlying QSlider widget.

        """
        self.widget = QSlider(self.parent_widget)

    def initialize(self, init_attrs):
        """ Initialize the widget's attributes.

        """
        super(QtSlider, self).initialize(init_attrs)
        self.set_value(init_attrs.get('value', 0))

    def bind(self):
        """ Bind the signal handlers for the widget.

        """
        self.widget.valueChanged.connect(self.on_value_changed)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_value(self, ctxt):
        """ Handle the 'set_value' message from the Enaml widget.

        """
        return self.set_value(ctxt['value'])

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_value_changed(self):
        """ Send the 'set_value' command to the Enaml widget when the 
        slider value has changed.

        """
        ctxt = {'value': self.widget.value()}
        self.send('set_value', ctxt)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_value(self, value):
        """ Set the value of the underlying widget.

        """
        self.widget.setValue(value)
        return True

