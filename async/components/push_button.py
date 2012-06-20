#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Str, Instance, Property, on_trait_change

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
    # Toolkit Communication
    #--------------------------------------------------------------------------
    @on_trait_change('icon, icon_size, text')
    def sync_object_state(self, name, new):
        """ Notify the client component of updates to the object state.

        """
        msg = 'set_' + name
        self.send(msg, {'value':new})

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(PushButton, self).initial_attrs()
        attrs = {
            'icon' : self.icon,
            'icon_size' : self.icon_size,
            'text' : self.text
        }
        super_attrs.update(attrs)
        return super_attrs
