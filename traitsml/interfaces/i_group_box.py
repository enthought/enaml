from traits.api import Bool, Enum, Str

from ..constants import Align
from .i_element import IElement


class IGroupBox(IElement):

    # The aligment of the title of the group box.
    alignment = Enum(Align.DEFAULT, *Align.values())

    # Whether or not the group box is checkable. Checking a 
    # group box will enable and disable its children.
    checkable = Bool

    # Whether or not the group box is checked.
    checked = Bool(True)

    # A flat group box will not draw sunkend or borders.
    flat = Bool

    # The title of the group box
    title = Str



