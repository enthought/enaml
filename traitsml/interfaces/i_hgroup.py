from traits.api import ReadOnly

from ..constants import Layout
from ..registry import register_element
from .i_element import IElement


@register_element
class IHGroup(IElement):
    # A convienence element with a hard-code HORIZONTAL layout
    layout = ReadOnly(Layout.HORIZONTAL)


