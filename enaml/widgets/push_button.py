from traits.api import Bool, Event, Str, Instance

from .control import Control, IControlImpl


class IPushButtonImpl(IControlImpl):

    def parent_text_changed(self, text):
        raise NotImplementedError
    

class PushButton(Control):
    """ A push button widget.

    Attributes
    ----------
    down : Bool
        Whether or not the button is currently pressed.

    text : Str
        The text to use as the button's label.

    clicked : Event
        Fired when the button is clicked.

    pressed : Event
        Fired when the button is pressed.

    released: Event
        Fired when the button is released.

    """
    down = Bool

    text = Str
    
    clicked = Event
    
    pressed = Event

    released = Event

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IPushButtonImpl)

