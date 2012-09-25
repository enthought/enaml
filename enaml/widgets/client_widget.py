#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str

from .proxy_widget import ProxyWidget
from .constraints_widget import ConstraintsWidget

class ClientWidget(ProxyWidget, ConstraintsWidget):
    """ A non-Enaml UI widget that is embedded in an Enaml UI
    
    A ClientWidget represents a UI widget that is outside the control of
    Enaml, but which is embedded as a child of an Enaml UI element and which
    is subject to contraints-based sizing.
    
    The expected behavior is that the client session object sill implement a
    method with the signature get_proxy_widget(proxy_id, parent), where `parent`
    is the toolkit widget instance that is from the Enaml parent. This method
    should return an appropriately parented toolkit widget.
    
    """
    pass