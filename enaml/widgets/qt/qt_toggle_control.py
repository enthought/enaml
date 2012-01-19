#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_control import QtControl

from ..toggle_control import AbstractTkToggleControl


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
        # If the label of the control changes, its size hint has likely
        # updated and the layout system needs to be informed
        self.shell_obj.size_hint_updated()
        
    def on_toggled(self):
        """ The event handler for the toggled event.

        """
        shell = self.shell_obj
        shell.checked = self.widget.isChecked()
        shell.toggled()

    def on_pressed(self):
        """ The event handler for the pressed event. Not meant for
        public consumption.

        """
        shell = self.shell_obj
        shell._down = True
        shell.pressed()

    def on_released(self):
        """ The event handler for the released event. Not meant for
        public consumption.

        """
        shell = self.shell_obj
        if shell._down:
            shell._down = False
            shell.released()

    def set_label(self, label):
        """ Sets the widget's label with the provided value. Not
        meant for public consumption.

        """
        self.widget.setText(label)

    def set_checked(self, checked):
        """ Sets the widget's checked state with the provided value.

        """
        widget = self.widget
        # This handles the case where, by default, Qt will not allow
        # all of the radio buttons in a group to be disabled. By 
        # temporarily turning off auto-exclusivity, we are able to
        # handle that case.
        if not checked and widget.isChecked() and widget.autoExclusive():
            widget.setAutoExclusive(False)
            widget.setChecked(checked)
            widget.setAutoExclusive(True)
        else:
            widget.setChecked(checked)

