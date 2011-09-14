import functools

from .qt import QtGui

from traits.api import Instance, implements

from .qt_component import QtComponent
from .styling import QtStyleHandler, qt_color

from ..control import IControlImpl


class QtControl(QtComponent):

    implements(IControlImpl)

    style_handler = Instance(QtStyleHandler)

    #---------------------------------------------------------------------------
    # IControlImpl interface
    #---------------------------------------------------------------------------
    
    def initialize_style(self):
        tags = {
            'background_color': qt_color,
        }
        style_handler = QtStyleHandler(widget=self.widget, tags=tags)
        style = self.parent.style
        
        for tag, converter in tags.items():
            value = style.get_property(tag)
            style_handler.set_style_value(value, tag, converter)

        style_handler.style_node = style
        self.style_handler = style_handler
 
    def layout_child_widgets(self):
        """ Ensures that the control does not contain children. Special
        control subclasses that do allow for children should reimplement
        this method.

        """
        if list(self.child_widgets()):
            raise ValueError('Standard controls cannot have children.')

