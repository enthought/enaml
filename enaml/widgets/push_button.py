from traits.api import Bool, Event, Str, Instance, Property

from .control import Control, IControlImpl


class IPushButtonImpl(IControlImpl):

    def parent_text_changed(self):
        raise NotImplementedError
    

class PushButton(Control):
    """ A push button widget.

    Attributes
    ----------
    down : Property(Bool)
        A read only property which indicates whether or not the button 
        is currently pressed.

    text : Str
        The text to use as the button's label.

    clicked : Event
        Fired when the button is clicked.

    pressed : Event
        Fired when the button is pressed.

    released: Event
        Fired when the button is released.

    _down : Bool
        A protected attribute that is used by the implementation object
        to set the value of down.

    """
    down = Property(Bool, depends_on='_down')

    text = Str
    
    clicked = Event
    
    pressed = Event

    released = Event

    _down = Bool

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IPushButtonImpl)

    def _get_down(self):
        """ The property getter for the 'down' attribute.

        """
        return self._down


PushButton.protect('_down', 'clicked', 'pressed', 'released')

