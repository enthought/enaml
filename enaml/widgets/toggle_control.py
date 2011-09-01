from traits.api import Bool, Event, Str

from .control import Control


class ToggleControl(Control):
    """ An abstract toggle element. 
    
    An element which toggles the value of a boolean field.

    Attributes
    ----------
    checked : Bool
        Whether the element is currently checked.

    down : Bool
        Whether the user is currently pressing the element.
        
    text : Str
        The text to use as the element's label.

    toggled : Event
        Fired when the element is toggled.

    pressed : Event
        Fired when the element is pressed.

    released : Event
        Fired when the element is released.

    """
    checked = Bool

    down = Bool

    text = Str
    
    toggled = Event
    
    pressed = Event

    released = Event

