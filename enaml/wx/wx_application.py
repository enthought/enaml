#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging

import wx

from enaml.application import Application

from .wx_action_socket import wxActionSocket, EVT_ACTION_SOCKET
from .wx_deferred_caller import wxDeferredCaller
from .wx_session import WxSession
from .wx_factories import register_default


logger = logging.getLogger(__name__)


# This registers the default Wx factories with the WxWidgetRegistry and
# allows an application access to the default widget implementations.
register_default()


class WxApplication(Application):
    """ A concrete implementation of an Enaml application.

    A WxApplication uses the Wx toolkit to implement an Enaml UI that
    runs in the local process.

    """
    def __init__(self, factories):
        """ Initialize a WxApplication.

        Parameters
        ----------
        factories : iterable
            An iterable of SessionFactory instances to pass to the
            superclass constructor.

        """
        super(WxApplication, self).__init__(factories)
        self._wxapp = wx.GetApp() or wx.PySimpleApp()
        self._wxcaller = wxDeferredCaller()
        self._wx_sessions = {}
        self._sockets = {}

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def socket(self, session_id):
        """ Get the ActionSocketInterface for a session.

        Parameters
        ----------
        session_id : str
            The string identifier for the session which will use the
            created action socket.

        Returns
        -------
        result : ActionSocketInterface
            An implementor of ActionSocketInterface which can be used
            by Enaml Sessione instances for messaging.

        """
        return self._socket_pair(session_id)[0]

    def start(self):
        """ Start the application's main event loop.

        """
        app = self._wxapp
        if not app.IsMainLoopRunning():
            app.MainLoop()

    def stop(self):
        """ Stop the application's main event loop.

        """
        app = self._wxapp
        if app.IsMainLoopRunning():
            app.Exit()

    def deferred_call(self, callback, *args, **kwargs):
        """ Invoke a callable on the next cycle of the main event loop
        thread.

        Parameters
        ----------
        callback : callable
            The callable object to execute at some point in the future.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        self._wxcaller.DeferredCall(callback, *args, **kwargs)

    def timed_call(self, ms, callback, *args, **kwargs):
        """ Invoke a callable on the main event loop thread at a
        specified time in the future.

        Parameters
        ----------
        ms : int
            The time to delay, in milliseconds, before executing the
            callable.

        callback : callable
            The callable object to execute at some point in the future.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        self._wxcaller.TimedCall(ms, callback, *args, **kwargs)

    def is_main_thread(self):
        """ Indicates whether the caller is on the main gui thread.

        Returns
        -------
        result : bool
            True if called from the main gui thread. False otherwise.

        """
        return wx.Thread_IsMain()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def start_session(self, name):
        """ Start a new session of the given name.

        This is an overridden parent class method which will build out
        the Wx client object tree for the session. It will be displayed
        when the application is started.

        """
        sid = super(WxApplication, self).start_session(name)
        socket = self._socket_pair(sid)[1]
        groups = self.session(sid).widget_groups[:]
        wx_session = WxSession(sid, groups)
        self._wx_sessions[sid] = wx_session
        wx_session.open(self.snapshot(sid), socket)
        return sid

    def end_session(self, session_id):
        """ End the session with the given session id.

        This is an overridden parent class method which will removes
        the references to the Wx client object trees for the session.

        """
        super(WxApplication, self).end_session(session_id)
        wx_session = self._wx_sessions.pop(session_id, None)
        if wx_session is not None:
            wx_session.close()
        self._sockets.pop(session_id, None)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _socket_pair(self, session_id):
        """ Get the socket pair for the given session id.

        If the socket pair does not yet exist, it will be created.

        Parameters
        ----------
        session_id : str
            The identifier of the session that will use the sockets.

        Returns
        -------
        result : tuple
            A 2-tuple of action sockets for the server and client sides,
            respectively.

        """
        sockets = self._sockets
        if session_id not in sockets:
            server_socket = wxActionSocket()
            client_socket = wxActionSocket()
            server_socket.Bind(EVT_ACTION_SOCKET, client_socket.receive)
            client_socket.Bind(EVT_ACTION_SOCKET, server_socket.receive)
            pair = (server_socket, client_socket)
            sockets[session_id] = pair
        else:
            pair = sockets[session_id]
        return pair

