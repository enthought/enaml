#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Str, Instance, Property

from .control import Control

from ..core.trait_types import CoercingInstance, EnamlEvent
from ..layout.geometry import Size
from ..noncomponents.abstract_icon import AbstractTkIcon


class PushButton(Control):
    """ A push button widget.

    """
    #: A read only property which indicates whether or not the button 
    #: is currently pressed.
    down = Property(Bool, depends_on='_down')

    #: The text to use as the button's label.
    text = Str

    #: The an icon to display in the button.
    icon = Instance(AbstractTkIcon)

    # The size of the icon
    icon_size = CoercingInstance(Size)
    
    #: Fired when the button is pressed and released.
    clicked = EnamlEvent
    
    #: Fired when the button is pressed.
    pressed = EnamlEvent

    #: Fired when the button is released.
    released = EnamlEvent
    
    #: How strongly a component hugs it's contents' width. PushButtons 
    #: hug their contents' width weakly.
    hug_width = 'weak'

    #: An internal attribute that is used by the implementation object
    #: to set the value of down.
    _down = Bool

    def _get_down(self):
        """ The property getter for the 'down' attribute.

        """
        return self._down

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(PushButton, self).bind()
        self.default_send_attr_bind(
                'icon', 'icon_size', 'text',
            )

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(PushButton, self).initial_attrs()
        attrs = {
            'icon' : self.icon,
            'icon_size' : self.icon_size,
            'text' : self.text,
        }
        super_attrs.update(attrs)
        return super_attrs

    #--------------------------------------------------------------------------
    # Toolkit Communication
    #--------------------------------------------------------------------------
    def receive_clicked(self, context):
        """ Callback from the UI when the control is clicked.

        """
        self.clicked()

    def receive_pressed(self, context):
        """ Callback from the UI when the control is pressed.

        """
        self.pressed()

    def receive_released(self, context):
        """ Callback from the UI when the control is released.

        """
        self.released()

    def receive_set_down(self, context):
        """ Callback from the UI when the button's down state changes

        """
        self._down = context['value']

