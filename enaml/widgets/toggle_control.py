#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Str, Instance, Property

from .control import Control
from ..core.trait_types import EnamlEvent


class ToggleControl(Control):
    """ An abstract toggle element. 
    
    An element which toggles the value of a boolean field. This is an 
    abstract class which should not be used directly. Rather, it provides
    common functionality for subclasses such as RadioButton, CheckBox and
    ToggleButton.

    """
    #: Whether the element is currently checked.
    checked = Bool

    #: A read only property which indicates whether the user is 
    #: currently pressing the element.
    down = Property(Bool, depends_on='_down')

    #: The text to use as the element's label.
    text = Str
    
    #: Fired when the element is toggled.
    toggled = EnamlEvent
    
    #: Fired when the element is pressed.
    pressed = EnamlEvent

    #: Fired when the element is released.
    released = EnamlEvent

    #: Internal storage for the down attribute
    _down = Bool
    
    #: How strongly a component hugs it's contents' width.
    #: Toggles hug their contents' width weakly by default.
    hug_width = 'weak'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(ToggleControl, self).bind()
        self.default_send_attr_bind('checked', 'text')

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(ToggleControl, self).initial_attrs()
        attrs = {
            'checked' : self.checked,
            'text': self.text,
        }
        super_attrs.update(attrs)
        return super_attrs

    #--------------------------------------------------------------------------
    # Toolkit Communication
    #--------------------------------------------------------------------------
    def receive_pressed(self, context):
        """ Callback from the UI when the control is pressed.

        """
        self.pressed()

    def receive_released(self, context):
        """ Callback from the UI when the control is released.

        """
        self.released()

    def receive_set_down(self, context):
        """ Callback from the UI when the down state of the control changes.

        """
        self._down = context["value"]

    def receive_toggled(self, context):
        """ Callback from the UI when the control is toggled.

        """
        self.toggled()

    #--------------------------------------------------------------------------
    # Property methods 
    #--------------------------------------------------------------------------
    def _get_down(self):
        """ The property getter for the 'down' attribute.

        """
        return self._down

