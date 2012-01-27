#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_control import QtControl

from ..push_button import AbstractTkPushButton


class QtPushButton(QtControl, AbstractTkPushButton):
    """ A Qt implementation of PushButton.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QPushButton control.

        """
        self.widget = QtGui.QPushButton(parent)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtPushButton, self).initialize()
        self.set_label(self.shell_obj.text)

    def bind(self):
        """ Connects the event handlers for the push button.

        """
        super(QtPushButton, self).bind()
        widget = self.widget
        widget.clicked.connect(self.on_clicked)
        widget.pressed.connect(self.on_pressed)
        widget.released.connect(self.on_released)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_text_changed(self, text):
        """ The change handler for the 'text' attribute.

        """
        self.set_label(text)
        # If the text of the button changes, the size hint has likely
        # change and the layout system needs to be informed.
        self.shell_obj.size_hint_updated()

    def on_clicked(self):
        """ The event handler for the button's clicked event.

        """
        shell = self.shell_obj
        shell._down = False
        shell.clicked()

    def on_pressed(self):
        """ The event handlers for the button's pressed event.

        """
        shell = self.shell_obj
        shell._down = True
        shell.pressed()

    def on_released(self):
        """ The event handler for the button's released event.

        """
        shell = self.shell_obj
        if shell._down:
            shell._down = False
            shell.released()

    def set_label(self, label):
        """ Sets the label on the button control.

        """
        self.widget.setText(label)

