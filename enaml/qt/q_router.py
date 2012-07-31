#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.utils import log_exceptions

from .qt.QtCore import QObject, Qt, Signal


class QRouter(QObject):
    """ A simple QObject subclass which assists in routing messages in
    a deferred fashion.

    """
    #: A signal emitted by a client instance when a message should 
    #: be sent to the Enaml Application instance. The payload of the
    #: signal is the Message object to be sent to the Application.
    appMessagePosted = Signal(object)

    #: A signal emitted by the request/push handler objects when a 
    #: message should be delivered to the QClient instance. The payload
    #: of the signal is the Message object to be sent to the client.
    clientMessagePosted = Signal(object)

    #: A signal emitted when a callback should be run on the event
    #: loop. The payload will be the callback tuple.
    callbackPosted = Signal(object)

    def __init__(self):
        """ Initialize a QRouter.

        """
        super(QRouter, self).__init__()
        self.callbackPosted.connect(
            self._onCallbackPosted, Qt.QueuedConnection
        )

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    @log_exceptions
    def _onCallbackPosted(self, item):
        """ The signal handler for the 'callbackPosted' signal.

        This handler is invoked via a Qt.QueuedConnection and hence
        will execute aynchronously. Exceptions raised in the callback
        will generate an error log.

        Parameters
        ----------
        item : 3-tuple
            The tuple of callback, args, kwargs emitted on the signal.
            
        """
        callback, args, kwargs = item
        callback(*args, **kwargs)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def addCallback(self, callback, *args, **kwargs):
        """ Add the callback to the queue to be run in the future.

        Parameters
        ----------
        callback : callable
            The callable to be run at some point in the future.

        *args, **kwargs
            The positional and keyword arguments to pass to the 
            callable when it is invoked.

        """
        item = (callback, args, kwargs)
        self.callbackPosted.emit(item)

