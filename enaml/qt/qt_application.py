#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging

from enaml.application import Application

from .qt.QtCore import Qt, QThread
from .qt.QtGui import QApplication
from .q_action_socket import QActionSocket
from .q_deferred_caller import QDeferredCaller
from .qt_session import QtSession
from .qt_factories import register_default


logger = logging.getLogger(__name__)


# This registers the default Qt factories with the QtWidgetRegistry and
# allows an application access to the default widget implementations.
register_default()


class QtApplication(Application):
    """ A concrete implementation of an Enaml application.

    A QtApplication uses the Qt toolkit to implement an Enaml UI that
    runs in the local process.

    """
    def __init__(self, factories):
        """ Initialize a QtApplication.

        Parameters
        ----------
        factories : iterable
            An iterable of SessionFactory instances to pass to the
            superclass constructor.

        """
        super(QtApplication, self).__init__(factories)
        self._qapp = QApplication.instance() or QApplication([])
        self._qcaller = QDeferredCaller()
        self._qt_sessions = {}
        self._sockets = {}

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def start_session(self, name):
        """ Start a new session of the given name.

        This method will create a new session object for the requested
        session type and return the new session_id. If the session name
        is invalid, an exception will be raised.

        Parameters
        ----------
        name : str
            The name of the session to start.

        Returns
        -------
        result : str
            The unique identifier for the created session.

        """
        sid = self.open_session(name)
        esock, qsock = self._socket_pair(sid)
        groups = self.session(sid).widget_groups[:]
        qt_session = QtSession(sid, groups)
        self._qt_sessions[sid] = qt_session
        qt_session.open(self.snapshot(sid), qsock)
        self.session(sid).activate(esock)
        return sid

    def end_session(self, sid):
        self.close_session(sid)
        qt_session = self._qt_sessions.pop(sid, None)
        if qt_session is not None:
            qt_session.close()
        self._sockets.pop(sid, None)

    def start(self):
        """ Start the application's main event loop.

        """
        app = self._qapp
        if not getattr(app, '_in_event_loop', False):
            app._in_event_loop = True
            app.exec_()
            app._in_event_loop = False

    def stop(self):
        """ Stop the application's main event loop.

        """
        app = self._qapp
        app.exit()
        app._in_event_loop = False

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
        self._qcaller.deferredCall(callback, *args, **kwargs)

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
        self._qcaller.timedCall(ms, callback, *args, **kwargs)

    def is_main_thread(self):
        """ Indicates whether the caller is on the main gui thread.

        Returns
        -------
        result : bool
            True if called from the main gui thread. False otherwise.

        """
        return QThread.currentThread() == self._qapp.thread()

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
            server_socket = QActionSocket()
            client_socket = QActionSocket()
            conn = Qt.QueuedConnection
            server_socket.messagePosted.connect(client_socket.receive, conn)
            client_socket.messagePosted.connect(server_socket.receive, conn)
            pair = (server_socket, client_socket)
            sockets[session_id] = pair
        else:
            pair = sockets[session_id]
        return pair

