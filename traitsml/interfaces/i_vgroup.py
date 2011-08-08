from traits.api import ReadOnly

from ..constants import Layout
from ..registry import register_element
from .i_element import IElement


@register_element
class IVGroup(IElement):
    # A an element with a static VERTICAL layout
    layout = ReadOnly(Layout.VERTICAL)


