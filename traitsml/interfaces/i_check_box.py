from traits.api import Bool, Event, Str

from .i_element import IElement


class ICheckBox(IElement):
    
    # Whether the button is currently checked
    checked = Bool

    # The text to show on the button
    text = Str
    
    # The event fired when the button is toggled
    toggled = Event
    
    # The event fired when the button is pressed
    pressed = Event

    # The event fired when the button is released
    released = Event


