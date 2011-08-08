from traits.api import Any, Bool, Enum, Event, Int, Str

from ..constants import Align
from .i_element import IElement


class ILineEdit(IElement):

    # The alignment of the text
    alignment = Enum(Align.DEFAULT, *Align.values())

    # The maximum length of the line edit, in characters - Int
    max_length = Int(-1)

    # Whether the line edit is read_only - Bool
    read_only = Bool

    # The text for the line edit
    text = Str

    # The Event emitted when the text is changed
    text_changed = Event

    # The Event emitted when the text is edited (not programatically changed)
    text_edited = Event


