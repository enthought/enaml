from enthought.traits.api import ReadOnly

from ..constants import Layout
from ..registry import register_element
from .element import Element


@register_element
class VGroup(Element):
    # A an element with a static VERTICAL layout
    layout = ReadOnly(Layout.VERTICAL)


