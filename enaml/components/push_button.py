#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Bool, Str, Instance, Property

from .control import Control, AbstractTkControl

from ..core.trait_types import CoercingInstance, EnamlEvent
from ..layout.geometry import Size
from ..noncomponents.abstract_icon import AbstractTkIcon


class AbstractTkPushButton(AbstractTkControl):
    """ The abstract toolkit interface for a PushButton.

    """
    @abstractmethod
    def shell_text_changed(self):
        """ The change handler for the 'text' attribute on the shell 
        component.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_icon_changed(self, icon):
        """ The change handler for the 'icon' attribute on the shell
        component.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_icon_size_changed(self, icon_size):
        """ The change handler for the 'icon_size' attribute on the shell
        component.

        """
        raise NotImplementedError


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

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkPushButton)

    def _get_down(self):
        """ The property getter for the 'down' attribute.

        """
        return self._down

