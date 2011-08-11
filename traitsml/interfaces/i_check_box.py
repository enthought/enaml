from traits.api import Bool, Event, Str

from .i_element import IElement


class ICheckBox(IElement):
    """ A check box widget.

    Attributes
    ----------
    checked : boolean. Whether or not the button is currently checked.

    text : string. The text to show next to the check box.

    toggled : event. Fired when the check box is toggled.

    pressed : event. Fired when the check box is pressed.

    released : event. Fired when the check box is released.

    """
    checked = Bool

    text = Str
    
    toggled = Event
    
    pressed = Event

    released = Event


