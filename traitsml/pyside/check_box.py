from enthought.traits.api import DelegatesTo

from PySide import QtGui

from .element import Element
from .mixins import GeneralWidgetMixin


class CheckBoxWidget(GeneralWidgetMixin, QtGui.QCheckBox):
    pass


class CheckBox(Element):
    
    # Whether the button is currently checked
    checked = DelegatesTo('abstract_obj')

    # The text to show on the button
    text = DelegatesTo('abstract_obj')
    
    # The event fired when the button is toggled
    toggled = DelegatesTo('abstract_obj')
    
    # The event fired when the button is pressed
    pressed = DelegatesTo('abstract_obj')

    # The event fired when the button is released
    released = DelegatesTo('abstract_obj')

    #--------------------------------------------------------------------------
    # Creation Handler
    #--------------------------------------------------------------------------
    def create_widget(self):
        return CheckBoxWidget()

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def init_widget(self):
        super(CheckBox, self).init_widget()
        widget = self.widget
        widget.toggled.connect(self._on_toggled)
        widget.pressed.connect(self._on_pressed)
        widget.released.connect(self._on_released)

    def init_attributes(self):
        super(CheckBox, self).init_attributes()
        self.init_checked()
        self.init_text()

    def init_checked(self):
        self.widget.setChecked(self.checked)

    def init_text(self):
        self.widget.setText(self.text)

    #--------------------------------------------------------------------------
    # Change handlers
    #--------------------------------------------------------------------------
    def _checked_changed(self):
        self.widget.setChecked(self.checked)

    def _text_changed(self):
        self.widget.setText(self.text)
        
    #--------------------------------------------------------------------------
    # Slots
    #--------------------------------------------------------------------------
    def _on_toggled(self):
        self.checked = self.widget.isChecked()
        self.toggled = True

    def _on_pressed(self):
        self.pressed = True

    def _on_released(self):
        self.released = True

    
