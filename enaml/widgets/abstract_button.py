#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Unicode, Property

from enaml.core.trait_types import EnamlEvent

from .constraints_widget import ConstraintsWidget


#: The button attributes to proxy to clients.
_AB_PROXY_ATTRS = ['text', 'checkable', 'checked']


class AbstractButton(ConstraintsWidget):
    """ A base class which provides functionality common for several
    button-like widgets.

    """
    #: The text to use as the button's label.
    text = Unicode

    #: The icon to use for the button.
    # icon = ...

    #: The size to use for the icon.
    # icon_size = ...

    #: Whether or not the button is checkable. The default is False.
    checkable = Bool(False)

    #: Whether a checkable button is currently checked.
    checked = Bool(False)

    #: A read only property which indicates whether the user is 
    #: currently pressing the element.
    down = Property(Bool, depends_on='_down')
    
    #: Fired when the button is pressed.
    pressed = EnamlEvent

    #: Fired when the button is released.
    released = EnamlEvent

    #: Fired when the button is pressed then released.
    clicked = EnamlEvent

    #: Fired when a checkable button is toggled.
    toggled = EnamlEvent

    #: Internal storage for the down attribute
    _down = Bool(False)
    
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

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(AbstractButton, self).initial_attrs()
        attrs = dict((attr, getattr(self, attr)) for attr in _AB_PROXY_ATTRS)
        super_attrs.update(attrs)
        return super_attrs

    #--------------------------------------------------------------------------
    # Toolkit Communication
    #--------------------------------------------------------------------------
    def receive_pressed(self, ctxt):
        """ Callback from the UI when the control is pressed.

        """
        self._down = True
        self.pressed()
        return True

    def receive_released(self, ctxt):
        """ Callback from the UI when the control is released.

        """
        self._down = False
        self.released()
        return True

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

    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    def _get_down(self):
        """ The property getter for the 'down' attribute.

        """
        return self._down

