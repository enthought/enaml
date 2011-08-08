from traits.api import ReadOnly

from ..constants import Layout
from .i_element import IElement


class IHGroup(IElement):
    # A convienence element with a hard-code HORIZONTAL layout
    layout = ReadOnly(Layout.HORIZONTAL)


