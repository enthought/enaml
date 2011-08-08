from traits.api import Any, Bool, Enum, Int, Str

from ..constants import Align
from .i_element import IElement


class ILabel(IElement):

    # The text in the label - Str
    text = Str
    
    # Whether text should wrap at word break - Bool
    wrap = Bool


