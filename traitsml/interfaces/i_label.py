from traits.api import Str

from .i_element import IElement


class ILabel(IElement):
    """ A simple read-only text display.

    Attributes
    ----------
    text = string. The text in the label.

    """
    text = Str
    

