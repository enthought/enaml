from traits.api import Instance

from .toggle_control import ToggleControl, IToggleControlImpl


class ICheckBoxImpl(IToggleControlImpl):
    pass


class CheckBox(ToggleControl):
    """ A check box widget derived from IToggleElement

    Use a check box when it's necessary to toggle a boolean value
    independent of any other widgets in the group. For allowing the
    toggling of only one value in a group of values, use a group
    of radio buttons.

    See Also
    --------
    IToggleElement

    """
    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    _impl = Instance(ICheckBoxImpl)

