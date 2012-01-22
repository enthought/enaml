#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_control import WXControl

from ..toggle_control import AbstractTkToggleControl


class WXToggleControl(WXControl, AbstractTkToggleControl):
    """ A base class for wxPython toggle widgets.

    This class can serve as a base class for widgets that implement
    toggle behavior such as CheckBox and RadioButton. It is not meant
    to be used directly. Subclasses should implement the 'create'
    and 'bind' methods.

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
        super(WXToggleControl, self).initialize()
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

    def on_toggled(self, event):
        """ The event handler for the toggled event.

        """
        shell = self.shell_obj
        shell.checked = self.widget.GetValue()
        shell._down = False
        shell.toggled()
        event.Skip()

    def on_pressed(self, event):
        """ The event handler for the pressed event.

        """
        shell = self.shell_obj
        shell._down = True
        shell.pressed()
        event.Skip()

    def on_released(self, event):
        """ The event handler for the released event.

        """
        shell = self.shell_obj
        if shell._down:
            shell._down = False
            shell.released()
        event.Skip()

    def set_label(self, label):
        """ Sets the widget's label with the provided value.

        """
        self.widget.SetLabel(label)

    def set_checked(self, checked):
        """ Sets the widget's checked state with the provided value.

        """
        self.widget.SetValue(checked)

