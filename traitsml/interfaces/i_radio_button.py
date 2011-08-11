from traits.api import Bool, Event, Str

from .i_element import IElement


class IRadioButton(IElement):
    """ A radio button widget. 
    
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
    
    Notes
    -----
    If multiple radio buttons are children of the same parent, 
    then only one of those radio buttons may be checked at a time.


    """
    checked = Bool

    text = Str
    
    toggled = Event
    
    pressed = Event

    released = Event
    

