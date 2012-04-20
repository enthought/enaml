#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance

from .toggle_control import ToggleControl, AbstractTkToggleControl

from ..core.trait_types import CoercingInstance
from ..layout.geometry import Size
from ..noncomponents.abstract_icon import AbstractTkIcon


class AbstractTkToggleButton(AbstractTkToggleControl):
    """ The abstract toolkit ToggleButton interface.

    """
    @abstractmethod
    def shell_icon_changed(self, icon):
        """ The change handler for the 'icon' attribute on the shell
        component.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_icon_size_changed(self, icon_size):
        """ The change handler for the 'icon_size' attribute on the 
        shell component.

        """
        raise NotImplementedError


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
    #: The an icon to display in the button.
    icon = Instance(AbstractTkIcon)

    #: The size of the icon.
    icon_size = CoercingInstance(Size)

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkToggleButton)

