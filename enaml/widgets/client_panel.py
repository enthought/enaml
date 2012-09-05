#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str

from .proxy_widget import ProxyWidget
from .widget_component import WidgetComponent

class ClientPanel(ProxyWidget, WidgetComponent):
    """ A non-Enaml UI widget that is embeds in an Enaml UI
    
    A ClientPanel represents a UI widget that is outside the control of
    Enaml, but which embeds an Enaml UI.
    
    The expected behavior is that the client session object sill implement a
    method with the signature get_proxy_widget(proxy_id, parent), where `parent`
    is None. This method should return a toolkit widget.
    
    It is presumed that the non-Enaml widget will provide layout for all its
    children, including those coming from Enaml.
    
    """
    pass