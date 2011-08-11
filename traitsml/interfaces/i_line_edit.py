from traits.api import Bool, Event, Int, Str

from .i_element import IElement


class ILineEdit(IElement):
    """ A single-line editable text widget.

    Attributes
    ----------
    max_length : Int
        The maximum length of the line edit in characters.

    read_only : Bool
        Whether or not the line edit is read only.

    text : Str
        The string to use in the line edit.

    text_changed : Event
        Fired when the text is changed programmatically,
        or by the user.

    text_edited : Event
        Fired when the text is changed by the user,
        and not changed programmatically.

    """
    max_length = Int(-1)

    read_only = Bool

    text = Str

    text_changed = Event

    text_edited = Event


