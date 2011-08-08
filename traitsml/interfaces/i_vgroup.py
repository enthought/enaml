from traits.api import ReadOnly

from ..constants import Layout
from .i_element import IElement


class IVGroup(IElement):
    # A an element with a static VERTICAL layout
    layout = ReadOnly(Layout.VERTICAL)


