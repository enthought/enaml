from enthought.traits.api import ReadOnly

from ..constants import Layout
from ..registry import register_element
from .element import Element


@register_element
class Form(Element):
    # A convienence element with a hard coded FORM layout
    layout = ReadOnly(Layout.FORM)


