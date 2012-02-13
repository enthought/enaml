#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Bool, Str, Instance, Property

from .control import Control, AbstractTkControl

from ..core.trait_types import EnamlEvent


class AbstractTkPushButton(AbstractTkControl):

    @abstractmethod
    def shell_text_changed(self):
        raise NotImplementedError
    

class PushButton(Control):
    """ A push button widget.

    """
    #: A read only property which indicates whether or not the button 
    #: is currently pressed.
    down = Property(Bool, depends_on='_down')

    #: The text to use as the button's label.
    text = Str
    
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

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkPushButton)

    def _get_down(self):
        """ The property getter for the 'down' attribute.

        """
        return self._down

