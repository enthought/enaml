#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str

from .messenger_widget import MessengerWidget

class ProxyWidget(MessengerWidget):
    """ A proxy of a non-Enaml UI widget
    
    An ProxyWidget represents a UI widget that is outside the control of
    Enaml.  The principal use is for embedding an Enaml UI inside a non-Enaml
    UI or vice-versa.
    
    The expected behavior is that the client session object sill implement a
    method with the signature get_proxy_widget(proxy_id, parent), where `parent`
    is either None or a toolkit widget instance that is controlled by Enaml.
    This method should return an appropriately parented toolkit widget.
    
    This class is not intended to be instantiated directly, rather code should
    use subclasses that expose more functionality based on the intended
    layout interactions with Enaml.
    
    """
    
    #: Arbitrary identifier for the proxied toolkit widget.  This will be used
    #: by the client session to find or create an appropriate client toolkit
    #: widget.
    proxy_id = Str
    
    # XXX how do we handle sizing?
    
    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the snapshot for a Window.

        """
        snap = super(ProxyWidget, self).snapshot()
        snap['proxy_id'] = self.proxy_id
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(ProxyWidget, self).bind()
