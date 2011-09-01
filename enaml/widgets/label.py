from traits.api import Str

from .control import Control


class Label(Control):
    """ A simple read-only text display.

    Attributes
    ----------
    text : Str
        The text in the label.

    """
    text = Str

