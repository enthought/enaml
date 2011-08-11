from traits.api import Any, Event, Enum

from .i_element import IElement
from ..constants import Buttons, Interaction


class IDialog(IElement):
    """ A basic dialog widget whose contents are user defined. 
    
    Attributes
    ----------
    interaction : Enum
        The window interaction type (e.g., modal).

    buttons : Enum
        One of a predefined list of button combinations.

    closed : Event
        Fired when the dialog is closed.

    result : Any
        The value that a dialog returns when it is closed.

    """
    interaction = Enum(Interaction.DEFAULT, *Interaction.values())

    # XXX - the button position should probably look
    # at the style.align attribute.

    buttons = Enum(Buttons.DEFAULT, *Buttons.values()) 

    closed = Event

    result = Any


