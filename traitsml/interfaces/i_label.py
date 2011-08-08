from traits.api import Any, Bool, Enum, Int, Str

from ..constants import Align
from ..registry import register_element
from .i_element import IElement


@register_element
class ILabel(IElement):
    
    # The alignment of the text in the label
    alignment = Enum(Align.DEFAULT, *Align.values())

    # The format of the text in the label - XXX create some enums
    format = Any
    
    # The number of pixels of indentation - Int
    indent = Int(-1)

    # The number of pixels of margin - Int
    margin = Int(-1)

    # The text in the label - Str
    text = Str
    
    # Whether text should wrap at word break - Bool
    wrap = Bool


