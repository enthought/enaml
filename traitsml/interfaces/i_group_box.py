from traits.api import Bool, Str

from .i_container import IContainer


class IGroupBox(IContainer):
    """ A container that can draw a border around its children.

    The GroupBox can draw an optional border around its child widgets.
    A GroupBox can also be checkable which will enable and disable its 
    children. The children of a GroupBox are layed out vertically, if
    this is not the desired behavior, use another container as the
    only child of the GroupBox which arranges the chilren as necessary.

    Attributes
    ----------
    border : Border Enum value
        Draw a border around the group according to the value of
        the Border enum.

    checkable : Bool
        Whether or not the group has a check box.

    checked : Bool
        If checkable, whether or not the box is checked. If a the 
        group box is checkable and the box unchecked, then all of
        the children in the group will be disabled.

    title: Str
        The title of the group box.

    """
    checkable = Bool

    checked = Bool

    title = Str

