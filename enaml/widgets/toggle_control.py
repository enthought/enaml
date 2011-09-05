from traits.api import Bool, Event, Str, Instance

from .control import Control, IControlImpl


class IToggleControlImpl(IControlImpl):
    
    def parent_checked_changed(self, checked):
        raise NotImplementedError
    
    def parent_text_changed(self, text):
        raise NotImplementedError


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

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IToggleControlImpl)

