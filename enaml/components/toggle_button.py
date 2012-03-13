#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance

from .toggle_control import ToggleControl, AbstractTkToggleControl


class AbstractTkToggleButton(AbstractTkToggleControl):
    """ The abstract toolkit ToggleButton interface.

    """
    pass


class ToggleButton(ToggleControl):
    """ A toggle button widget.

    A toggle button stays down when pressed and returns to the up 
    position when pressed again. It encapsulates the functionality of
    a CheckBox in the form of a PushButton.

    Use a toggle button when it's necessary to toggle a boolean value
    independent of any other widgets in the group. For allowing the 
    toggling of only one value in a group of values, use a group of 
    radio buttons.

    See Also
    --------
    ToggleControl

    """
    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkToggleButton)

