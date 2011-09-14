from traits.api import implements

from .qt_control import QtControl

from ..toggle_control import IToggleControlImpl


class QtToggleControl(QtControl):
    """ A base class for PySide toggle widgets.

    This class can serve as a base class for widgets that implement
    toggle behavior such as CheckBox and RadioButton. It is not meant
    to be used directly. Subclasses should implement the 'create_widget'
    method.

    See Also
    --------
    IToggleElement

    """
    implements(IToggleControlImpl)

    #---------------------------------------------------------------------------
    # IToggleControlImpl interface
    #---------------------------------------------------------------------------
    def initialize_widget(self):
        """ Initializes the attributes of the underlying control. Not
        meant for public consumption.

        """
        parent = self.parent
        self.set_label(parent.text)
        self.set_checked(parent.checked)
        self.bind()

    def parent_checked_changed(self, checked):
        """ The change handler for the 'checked' attribute. Not meant
        for public consumption.

        """
        self.set_checked(checked)

    def parent_text_changed(self, text):
        """ The change handler for the 'text' attribute. Not meant
        for public consumption.

        """
        self.set_label(text)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def bind(self):
        """ Binds the event handlers of the control. Must be implemented
        by subclasses.

        """
        raise NotImplementedError

    def on_toggled(self):
        """ The event handler for the toggled event. Not meant for
        public consumption.

        """
        parent = self.parent
        parent.checked = self.widget.isChecked()
        parent.toggled = True

    def on_pressed(self):
        """ The event handler for the pressed event. Not meant for
        public consumption.

        """
        parent = self.parent
        parent._down = True
        parent.pressed = True

    def on_released(self):
        """ The event handler for the released event. Not meant for
        public consumption.

        """
        
        parent = self.parent
        parent._down = False
        parent.released = True

    def set_label(self, label):
        """ Sets the widget's label with the provided value. Not 
        meant for public consumption.

        """
        self.widget.setText(label)

    def set_checked(self, checked):
        """ Sets the widget's checked state with the provided value.
        Not meant for public consumption.

        """
        self.widget.setDown(checked)

