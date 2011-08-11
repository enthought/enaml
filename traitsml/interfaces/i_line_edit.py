from traits.api import Bool, Event, Int, Str

from .i_element import IElement


class ILineEdit(IElement):
    """ A single line editable text widget.

    Attributes
    ----------
    max_length : int. The maximum length of the line edit in characters.

    read_only : bool. Whether or not the line edit is read only.

    text : string. The string to use in the line edit.

    text_changed : event. Fired when the text is changed by the user
                   or programmatically changed.

    text_edited : event. Fired when the text is changed by the user
                  but not programmatically changed.

    """
    max_length = Int(-1)

    read_only = Bool

    text = Str

    text_changed = Event

    text_edited = Event


