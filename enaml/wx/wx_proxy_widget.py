#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_messenger_widget import WxMessengerWidget

class WxProxyWidget(WxMessengerWidget):
    """ A Wx implementation of an Enaml ProxyWidget.

    """
    #: The storage for the toolkit widget id
    _proxy_id = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ The defer to the session to acquire the local Wx proxy widget.

        """
        return self._session.get_proxy_widget(self, parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        self.set_proxy_id(tree['proxy_id'])
        super(WxProxyWidget, self).create(tree)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------

    def set_proxy_id(self, proxy_id):
        """ Set the proxy id for the window.

        """
        self._proxy_id = proxy_id

