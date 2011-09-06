from traits.api import Bool, Event, Str, Instance, Property

from .control import Control, IControlImpl

from ..util.decorators import protected


class IToggleControlImpl(IControlImpl):
    
    def parent_checked_changed(self, checked):
        raise NotImplementedError
    
    def parent_text_changed(self, text):
        raise NotImplementedError


@protected('_down')
class ToggleControl(Control):
    """ An abstract toggle element. 
    
    An element which toggles the value of a boolean field. This is an
    abstract class which should not be used directly. Rather, it provides
    common functionality of subclasses such as RadioButton and CheckBox.

    Attributes
    ----------
    checked : Bool
        Whether the element is currently checked.

    down : Property(Bool)
        A read only property which indicates whether the user is 
        currently pressing the element.
        
    text : Str
        The text to use as the element's label.

    toggled : Event
        Fired when the element is toggled.

    pressed : Event
        Fired when the element is pressed.

    released : Event
        Fired when the element is released.

    _down : Bool
        A protected attribute used by the implementation object to
        set the value of down.

    """
    checked = Bool

    down = Property(Bool, depends_on='_down')

    text = Str
    
    toggled = Event
    
    pressed = Event

    released = Event

    _down = Bool

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IToggleControlImpl)

    def _get_down(self):
        """ The property getter for the 'down' attribute.

        """
        return self._down

