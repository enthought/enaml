from traits.api import Any, Event, Enum

from .i_element import IElement
from ..constants import Buttons, Interaction


class IDialog(IElement):
    """ A basic dialog widget whose contents are user defined. 
    
    Attributes
    ----------
    interaction : An Interaction enum value.

    buttons : A Buttons enum value.

    closed : event. Fired when the dialog is closed.

    result : The value returned by the dialog when it's closed.

    """
    interaction = Enum(Interaction.DEFAULT, *Interaction.values())

    # XXX - the button position should probably look
    # at the style.align attribute.

    buttons = Enum(Buttons.DEFAULT, *Buttons.values()) 

    closed = Event

    result = Any


