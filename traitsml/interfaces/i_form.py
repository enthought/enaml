from traits.api import ReadOnly

from ..constants import Layout
from ..registry import register_element
from .i_element import IElement


@register_element
class IForm(IElement):
    # A convienence element with a hard coded FORM layout
    layout = ReadOnly(Layout.FORM)


