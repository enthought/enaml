from enthought.traits.api import DelegatesTo, Instance

from PySide import QtGui

from .element import Element
from .mixins import GeneralWidgetMixin


class PushButtonWidget(GeneralWidgetMixin, QtGui.QPushButton):
    pass


class PushButton(Element):
    
    # Whether the button is currently pressed - Bool
    down = DelegatesTo('abstract_obj')

    # The text to show on the button - Str
    text = DelegatesTo('abstract_obj')
    
    # The event fired when the button is clicked
    clicked = DelegatesTo('abstract_obj')
    
    # The event fired when the button is pressed
    pressed = DelegatesTo('abstract_obj')

    # The event fired when the button is released
    released = DelegatesTo('abstract_obj')
    
    #--------------------------------------------------------------------------
    # Creation Handler
    #--------------------------------------------------------------------------
    def create_widget(self):
        return PushButtonWidget()

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def init_widget(self):
        super(PushButton, self).init_widget()
        widget = self.widget
        widget.clicked.connect(self._on_clicked)
        widget.pressed.connect(self._on_pressed)
        widget.released.connect(self._on_released)
    
    def init_attributes(self):
        super(PushButton, self).init_attributes()
        self.init_down()
        self.init_text()
    
    def init_down(self):
        self.widget.setDown(self.down)

    def init_text(self):
        self.widget.setText(self.text)

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def _down_changed(self):
        self.widget.setDown(self.down)
    
    def _text_changed(self):
        self.widget.setText(self.text)

    #--------------------------------------------------------------------------
    # Signal Connections
    #--------------------------------------------------------------------------
    def _on_clicked(self):
        self.clicked = True

    def _on_pressed(self):
        self.down = self.widget.isDown()
        self.pressed = True

    def _on_released(self):
        self.down = self.widget.isDown()
        self.released = True

 
