#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from base64 import b64encode

from traits.api import Bool, Unicode, Tuple, Instance

from enaml.core.trait_types import EnamlEvent

from .constraints_widget import ConstraintsWidget
from .icon import Icon


#: The button attributes to proxy to clients.
_BUTTON_ATTRS = ['text', 'checkable', 'checked', 'icon_size']


class AbstractButton(ConstraintsWidget):
    """ A base class which provides functionality common for several
    button-like widgets.

    """
    #: The text to use as the button's label.
    text = Unicode

    #: The icon to use for the button.
    icon = Instance(Icon)

    #: The size to use for the icon.
    icon_size = Tuple

    #: Whether or not the button is checkable. The default is False.
    checkable = Bool(False)

    #: Whether a checkable button is currently checked.
    checked = Bool(False)

    #: Fired when the button is pressed then released. The payload will
    #: be the current checked state.
    clicked = EnamlEvent

    #: Fired when a checkable button is toggled. The payload will be
    #: the current checked state.
    toggled = EnamlEvent
    
    #: How strongly a component hugs it's contents' width. Buttons hug
    #: their contents' width weakly by default.
    hug_width = 'weak'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def creation_attributes(self):
        """ Returns the creation attributes for an abstract button.

        """
        super_attrs = super(AbstractButton, self).creation_attributes()
        attrs = dict((attr, getattr(self, attr)) for attr in _BUTTON_ATTRS)
        super_attrs.update(attrs)
        icon = self.icon
        super_attrs['icon'] = b64encode(icon.data()) if icon else None
        return super_attrs

    def bind(self):
        """ Bind the change handlers for an abstract button.

        """
        super(AbstractButton, self).bind()
        self.publish_attributes(*_BUTTON_ATTRS)
        self.on_trait_change(self.send_icon, 'icon')

    def send_icon(self):
        """ Send the icon data to the Enaml widget, encoded in base 64 format

        """
        icon = self.icon
        enc_data = b64encode(icon.data()) if icon else None
        self.send_message({'action': 'set-icon','icon': enc_data})
        
    #--------------------------------------------------------------------------
    # Toolkit Communication
    #--------------------------------------------------------------------------
    def on_message_clicked(self, payload):
        """ Handle the 'clicked' action from the UI widget. The payload
        will contain the current checked state.

        """
        checked = payload['checked']
        self.set_guarded(checked=checked)
        self.clicked(checked)

    def on_message_toggled(self, payload):
        """ Callback from the UI when the control is toggled. The payload
        will contain the current checked state.

        """
        checked = payload['checked']
        self.set_guarded(checked=checked)
        self.toggled(checked)

