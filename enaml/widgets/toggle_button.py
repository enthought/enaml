#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance

from .toggle_control import ToggleControl

from ..core.trait_types import CoercingInstance
from ..layout.geometry import Size
from ..noncomponents.abstract_icon import AbstractTkIcon


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

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(ToggleButton, self).bind()
        self.default_send('icon', 'icon_size')

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(ToggleButton, self).initial_attrs()
        attrs = {
            'icon' : self.icon,
            'icon_size': self.icon_size,
        }
        super_attrs.update(attrs)
        return super_attrs

