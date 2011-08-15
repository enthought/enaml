from traits.api import Bool, Event, Str

from .i_element import IElement


class ICheckBox(IElement):
    """ A check box widget.

    Use a check box when it's necessary to toggle a boolean value
    independent of any other widgets in the group. For allowing the
    toggling of only one value in a group of values, use a group
    of radio buttons.

    Attributes
    ----------
    checked : Bool
        Whether or not the button is currently checked.

    text : Str
         The text to show next to the check box.

    toggled : Event
        Fired when the check box is toggled.

    pressed : Event
        Fired when the check box is pressed.

    released : Event
        Fired when the check box is released.

    """
    checked = Bool

    text = Str
    
    toggled = Event
    
    pressed = Event

    released = Event

