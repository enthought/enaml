#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QPushButton
from .qt_constraints_widget import QtConstraintsWidget


class QtPushButton(QtConstraintsWidget):
    """ A Qt4 implementation of an Enaml Slider.

    """
    def create(self):
        """ Create the underlying QSlider widget.

        """
        self.widget = QPushButton(self.parent_widget)

    def initialize(self, init_attrs):
        """ Initialize the widget's attributes.

        """
        super(QtPushButton, self).initialize(init_attrs)
        self.set_text(init_attrs.get('text', u''))

    def bind(self):
        """ Bind the signal handlers for the widget.

        """
        widget = self.widget
        widget.clicked.connect(self.on_clicked)
        widget.pressed.connect(self.on_pressed)
        widget.released.connect(self.on_released)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_text(self, ctxt):
        """ Handle the 'set_text' message from the Enaml widget.

        """
        return self.set_text(ctxt.get('value', u''))

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_clicked(self):
        """ Send the 'clicked' command to the Enaml widget when the 
        button is clicked.

        """
        self.send('clicked', {})
    
    def on_pressed(self):
        """ Send the 'pressed' command to the Enaml widget when the 
        button is pressed.

        """
        self.send('pressed', {})

    def on_released(self):
        """ Send the 'released' command to the Enaml widget when the 
        button is released.

        """
        self.send('released', {})

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the text of the underlying widget.

        """
        self.widget.setText(text)
        return True

