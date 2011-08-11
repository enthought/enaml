from traits.api import Bool, Event, Str

from .i_element import IElement


class ICheckBox(IElement):
    """ A check box widget.

    Attributes
    ----------
    checked : Bool
        Whether or not the button is currently checked.

    text : Str
         The text to show next to the check box.

    toggled : Event
        Fired when the check box is toggled.

    pressed : Event
        Fired when the check box is pressed.

    released : Event
        Fired when the check box is released.

    """
    checked = Bool

    text = Str
    
    toggled = Event
    
    pressed = Event

    released = Event


