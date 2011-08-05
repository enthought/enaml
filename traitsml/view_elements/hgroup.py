from enthought.traits.api import ReadOnly

from ..constants import Layout
from ..registry import register_element
from .element import Element


@register_element
class HGroup(Element):
    # A convienence element with a hard-code HORIZONTAL layout
    layout = ReadOnly(Layout.HORIZONTAL)


