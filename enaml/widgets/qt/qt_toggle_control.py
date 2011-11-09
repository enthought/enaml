#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_control import QtControl

from ..toggle_control import AbstractTkToggleControl

# FIXME: I do not like that there are methods in this class that assume
# a specific behaviour for the widget. And that we ask the developer to
# bind to such functions. Are we pushing the `remove dublication` rule
# too much?
class QtToggleControl(QtControl, AbstractTkToggleControl):
    """ A base class for Qt toggle widgets.

    This class can serve as a base class for widgets that implement
    toggle behavior such as CheckBox and RadioButton. It is not meant
    to be used directly. Subclasses should implement the 'create'
    and bind methods.

    Furthermore, the toggled, pressed and released event that is generated
    by the toolkit widget needs to be bound to the on_toggled(),
    on_pressed() and on_released() methods.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def initialize(self):
        """ Initializes the attributes of the underlying control.

        """
        super(QtToggleControl, self).initialize()
        shell = self.shell_obj
        self.set_label(shell.text)
        self.set_checked(shell.checked)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_checked_changed(self, checked):
        """ The change handler for the 'checked' attribute.

        """
        self.set_checked(checked)

    def shell_text_changed(self, text):
        """ The change handler for the 'text' attribute.

        """
        self.set_label(text)

    def on_toggled(self):
        """ The event handler for the toggled event.

        """
        shell = self.shell_obj
        shell.checked = self.widget.isChecked()
        shell.toggled = True

    def on_pressed(self):
        """ The event handler for the pressed event. Not meant for
        public consumption.

        """
        shell = self.shell_obj
        shell._down = True
        shell.pressed = True

    def on_released(self):
        """ The event handler for the released event. Not meant for
        public consumption.

        """
        shell = self.shell_obj
        if shell._down:
            shell._down = False
            shell.released = True

    def set_label(self, label):
        """ Sets the widget's label with the provided value. Not
        meant for public consumption.

        """
        self.widget.setText(label)

    def set_checked(self, checked):
        """ Sets the widget's checked state with the provided value.
        Not meant for public consumption.

        """
        self.widget.setChecked(checked)

