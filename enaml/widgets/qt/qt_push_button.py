#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui

from traits.api import implements

from .qt_control import QtControl

from ..push_button import IPushButtonImpl


class QtPushButton(QtControl):
    """ A Qt implementation of PushButton.

    See Also
    --------
    PushButton

    """
    implements(IPushButtonImpl)

    #---------------------------------------------------------------------------
    # IPushButtonImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying QPushButton control.

        """
        self.widget = QtGui.QPushButton(self.parent_widget())
        
    def initialize_widget(self):
        """ Intializes the widget with the attributes of this instance.

        """
        self.set_label(self.parent.text)
        self.bind()

    def parent_text_changed(self, text):
        """ The change handler for the 'text' attribute. Not meant for
        public consumption.

        """
        self.set_label(text)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def bind(self):
        """ Binds the event handlers for the push button.

        """
        widget = self.widget
        widget.clicked.connect(self.on_clicked)
        widget.pressed.connect(self.on_pressed)
        widget.released.connect(self.on_released)

    def on_clicked(self):
        """ The event handler for the button's clicked event. Not meant
        for public consumption.

        """
        parent = self.parent
        parent._down = False
        parent.clicked = True

    def on_pressed(self):
        """ The event handlers for the button's pressed event. Not meant
        for public consumption.

        """
        parent = self.parent
        parent._down = True
        parent.pressed = True

    def on_released(self):
        """ The event handler for the button's released event. Not
        meant for public consumption.

        """
        parent = self.parent
        if parent._down:
            parent._down = False
            parent.released = True

    def set_label(self, label):
        """ Sets the label on the button control. Not meant for public
        consumption.

        """
        self.widget.setText(label)
