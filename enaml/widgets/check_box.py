#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance

from .toggle_control import ToggleControl, AbstractTkToggleControl


class AbstractTkCheckBox(AbstractTkToggleControl):
    pass


class CheckBox(ToggleControl):
    """ A check box widget.

    Use a check box when it's necessary to toggle a boolean value
    independent of any other widgets in the group. For allowing the
    toggling of only one value in a group of values, use a group
    of radio buttons.

    See Also
    --------
    ToggleControl

    """
    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkCheckBox)

