#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.request import BaseRequest, BasePushHandler
from enaml.utils import log_exceptions

import wx

from .wx_factories import WX_FACTORIES
from .wx_local_client import WxLocalClient
from .wx_router import wxRouter, EVT_APP_MESSAGE


class WxLocalRequest(BaseRequest):
    """ A concrete BaseRequest implementation for the WxLocalServer.

    """
    def __init__(self, message, router):
        """ Initialize a WxLocalRequest.

        Parameters
        ----------
        message : Message
            The Message instance that generated this request.

        router : wxRouter
            The wxRouter instance with which to issue replies and 
            callbacks.

        """
        self._message = message
        self._router = router
        self._finished = False

    #--------------------------------------------------------------------------
    # Abstract API implementation
    #--------------------------------------------------------------------------
    @property
    def message(self):
        """ The Message object for this request.

        Returns
        -------
        result : Message
            The Message instance pertaining to this request.

        """
        return self._message

    def add_callback(self, callback, *args, **kwargs):
        """ Add a callback to the event queue to be called later.

        This is can be used by the request handlers to defer long 
        running work until a future time, at which point the results
        can be pushed to the client with the 'push_handler()'.

        Parameters
        ----------
        callback : callable
            A callable which should be invoked by the event loop at 
            some future time. This method will return immediately.

        *args, **kwargs
            The positional and keyword arguments to pass to the 
            callable when it is invoked.

        """
        self._router.AddCallback(callback, *args, **kwargs)

    @log_exceptions
    def send_response(self, message):
        """ Send the given message to the client as a reply.

        Parameters
        ----------
        message : Message
            A Message instance to send to the client as a reply to
            this particular request.

        """
        if self._finished:
            raise RuntimeError('Request already finished')
        self._router.PostClientMessage(message)
        self._finished = True

    def push_handler(self):
        """ Returns an object that can be used to push unsolicited 
        messages to this client.

        Returns
        -------
        result : QtLocalPushHandler
            A QtLocalPushHandler instance which can be used to push 
            messages to this client, without the client initiating a 
            request.

        """
        return WxLocalPushHandler(self._router)


class WxLocalPushHandler(BasePushHandler):
    """ A concrete BasePushHandler implementation for the WxLocalServer.

    Instances of this class will remain functional for the lifetime
    of the originating client. If the client disconnects, then this
    handler will silently drop the messages.

    """
    def __init__(self, router):
        """ Initialize a WxLocalPushHandler.

        Parameters
        ----------
        router : wxRouter
            The wxRouter instance with which to issue requests and 
            callbacks.

        """
        self._router = router

    def push_message(self, message):
        """ Push the given message to the client.

        Parameters
        ----------
        message : Message
            The Message instance that should be pushed to the client.

        """
        self._router.PostClientMessage(message)

    def add_callback(self, callback, *args, **kwargs):
        """ Add a callback to the event queue to be called later.

        This is used as a convenience for Session objects to provide
        a way to run callables in a deferred fashion. It does not 
        imply any communication with the client. It is merely an
        abstract entry point into the zmq event loop. 

        Call it a concession to practicality over purity - SCC

        Parameters
        ----------
        callback : callable
            A callable which should be invoked by the event loop at 
            some future time. This method returns immediately.

        *args, **kwargs
            The positional and keyword arguments to pass to the 
            callable when it is invoked.

        """
        self._router.AddCallback(callback, *args, **kwargs)


class WxLocalServer(object):
    """ An Enaml Application server which executes in the local process
    and uses Wx to create the client items.

    Since this is a locally running in-process server, the Enaml 
    messages skip the serialization to JSON step.

    """
    def __init__(self, app, factories=None):
        """ Initialize a WxLocalServer.

        Parameters
        ----------
        app : Application
            The Enaml application object that should be served.

        factories : dict, optional
            A dictionary of client widget factories to use for the
            application. If not provided, the defaults will be used.

        """
        super(WxLocalServer, self).__init__()

        # The internal Wx application object, this gets created before
        # any other Wx objects
        self._wxapp = wx.GetApp() or wx.PySimpleApp()

        # The enaml application that is being served by this server.
        self._app = app

        # The QRouter to use for message passing.
        self._router = wxRouter()
        self._router.Bind(EVT_APP_MESSAGE, self._on_app_message_posted)

        # The local client that will manage the qt client sessions
        self._client = WxLocalClient(self._router, factories or WX_FACTORIES)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    @log_exceptions
    def _on_app_message_posted(self, event):
        """ A handler for the 'EVT_APP_MESSAGE' event on the wxRouter.

        This method will be invoked when the client needs to send a 
        message to the Enaml application.

        Parameters
        ----------
        message : Message
            The message object to pass to the Enaml Application.

        """
        request = WxLocalRequest(event.message, self._router)
        self._app.handle_request(request)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def local_client(self):
        """ Return a handle to the local client instance for the server.

        Since this is a locally running server, there is a singleton
        instance of QtLocalClient that is used to manage the qt view
        sessions.

        Returns
        -------
        result : QtLocalClient
            The singleton local client instance used for managing the
            local qt session objects. The 'start_session' method on
            this object should be used to start a new view session.

        """
        return self._client

    def start(self):
        """ Start the sever's main loop.

        This will enter the main GUI event loop and block until a call
        to 'stop' is made, at which point this method will return.

        """
        app = self._wxapp
        if not app.IsMainLoopRunning():
            self._client.startup()
            f = wx.Frame(None)
            wx.CallAfter(f.Destroy)
            app.MainLoop()

    def stop(self):
        """ Stop the server's main loop.

        Calling this method will cause a previous call to 'start' to 
        unblock and return.

        """
        app = self._wxapp
        if app.IsMainLoopRunning():
            app.ExitMainLoop()

