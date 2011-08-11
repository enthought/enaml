from traits.api import Bool, Str

from .i_element import IElement


class IGroupBox(IElement):
    """ A collection of widgets with optional title, check box
    and border.

    Attributes
    ----------
    checkable : bool. Whether or not the group has a check box.

    checked : bool. If checkable, whether or not the box is checked.
              If a checkable box is unchecked, all children will be
              disabled.

    title: string. The title of the check box.

    """
    checkable = Bool

    # Whether or not the group box is checked.
    checked = Bool(True)

    # The title of the group box
    title = Str


