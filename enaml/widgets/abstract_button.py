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
_AB_PROXY_ATTRS = ['text', 'checkable', 'checked','icon_size']


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

    #: Fired when the button is pressed then released.
    clicked = EnamlEvent

    #: Fired when a checkable button is toggled.
    toggled = EnamlEvent
    
    #: How strongly a component hugs it's contents' width. Buttons hug
    #: their contents' width weakly by default.
    hug_width = 'weak'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(AbstractButton, self).bind()
        self.default_send(*_AB_PROXY_ATTRS)
        self.on_trait_change(self.send_icon, 'icon')

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(AbstractButton, self).initial_attrs()
        attrs = dict((attr, getattr(self, attr)) for attr in _AB_PROXY_ATTRS)
        super_attrs.update(attrs)
        super_attrs.update({'icon':b64encode(self.icon.data())})
        return super_attrs

    def send_icon(self):
        """ Send the icon data to the Enaml widget, encoded in base 64 format

        """
        enc_data = b64encode(self.icon.data())
        self.send({'action':'set_icon','icon':enc_data})
        
    #--------------------------------------------------------------------------
    # Toolkit Communication
    #--------------------------------------------------------------------------
    def receive_clicked(self, ctxt):
        """ Callback from the UI when the control is clicked. The ctxt
        will contain the current checked state.

        """
        checked = ctxt['checked']
        self.set_guarded(checked=checked)
        self.clicked(checked)
        return True

    def receive_toggled(self, ctxt):
        """ Callback from the UI when the control is toggled. The ctxt
        will contain the current checked state.

        """
        checked = ctxt['checked']
        self.set_guarded(checked=checked)
        self.toggled(checked)
        return True
