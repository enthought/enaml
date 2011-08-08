from traits.api import Bool, Event, Str

from .i_element import IElement


class IPushButton(IElement):
    
    # Whether the button is currently pressed - Bool
    down = Bool

    # The text to show on the button - Str
    text = Str
    
    # The event fired when the button is clicked - Event
    clicked = Event
    
    # The event fired when the button is pressed - Event
    pressed = Event

    # The event fired when the button is released - Event
    released = Event


