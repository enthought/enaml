from traits.api import Bool, Event, Str

from .i_element import IElement


class IRadioButton(IElement):
    """ A radio button widget. 
    
    Use a radio button to toggle the value of a boolean field.
    Use a group of radio buttons to toggle between multiple 
    values when only one value of the group can be selected 
    at a time.

    Attributes
    ----------
    checked : Bool
        Whether the button is currently checked.

    text : Str
        The text to use as the button's label.

    toggled : Event
        Fired when the button is toggled.

    pressed : Event
        Fired when the button is pressed.

    released : Event
        Fired when the button is released.

    """
    checked = Bool

    text = Str
    
    toggled = Event
    
    pressed = Event

    released = Event

