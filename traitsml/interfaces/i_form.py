from traits.api import ReadOnly

from ..constants import Layout
from .i_element import IElement


class IForm(IElement):
    # A convienence element with a hard coded FORM layout
    layout = ReadOnly(Layout.FORM)


