#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Property

from .window import Window

from ..core.trait_types import EnamlEvent
from ..enums import DialogResult, Modality

_DIALOG_PROXY_ATTRS = ['modality', 'visible']

class Dialog(Window):
    """ A Window subclass which adds modal style behavior.

    The basic dialog has no buttons, but provides methods for the
    accept and reject behavior for the dialog.

    """
    #: A read only property which will be True when the dialog is open, 
    #: False otherwise.
    active = Property(Bool, depends_on='_active')

    #: Override widget_components visible attribute so that the dialog does
    #: not show when prepare() is called
    visible = Bool(False)

    #: Fired when the dialog is opened.
    opened = EnamlEvent

    #: Fired when the dialog is closed. The event payload will be the 
    #: dialog result.
    closed = EnamlEvent

    #: A read only property which is set to the result of the dialog; 
    #: 'rejected' if rejected() was called or the window was closed via 
    #: the 'x' window button, 'accepted' if accept() was called. The 
    #: result is set before the 'closed' event is fired.
    result = Property(DialogResult, depends_on='_result')

    #: An enum which indicates the modality of the dialog. One of 
    #: 'application_modal' or 'window_modal'. The default value is 
    #: 'application_modal'. Changes to this attribute *after* the 
    #: dialog is shown will have no effect.
    modality = Modality
    
    #: An internal trait used to store the active state of the dialog.
    _active = Bool(False)

    #: An internal trait used to store the result of the dialog.
    _result = DialogResult('rejected')
        
    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    def _get_active(self):
        """ The property getter for the 'active' attribute.

        """
        return self._active

    def _get_result(self):
        """ The property getter for the 'result' attribute.

        """
        return self._result
   
    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Dialog, self).bind()
        self.default_send(*_DIALOG_PROXY_ATTRS)

    def initial_attrs(self):
        """ Return the attr initialization dict for a window.

        """
        super_attrs = super(Dialog, self).initial_attrs()
        get = getattr
        attrs = dict((attr, get(self, attr)) for attr in _DIALOG_PROXY_ATTRS)
        super_attrs.update(attrs)
        return super_attrs

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def accept(self):
        """ Close the dialog and set the result to `accepted`.

        Call this method to trigger the same behavior as clicking on an
        Ok button.

        """
        self.send({'action':'accept'})

    def reject(self):
        """ Close the dialog and set the result to `rejected`.

        Call this method to trigger the same behavior as clicking on a
        Cancel button.

        """
        self.send({'action':'reject'})

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_closed(self, ctxt):
        """ Message handler for closed

        """
        self._active = False
        self._result = ctxt['result']

    def receive_set_active(self, ctxt):
        """ Message handler for set_active

        """
        self._active = ctxt['value']
