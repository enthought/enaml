#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import defaultdict

from enaml.application import Application

from .qt.QtCore import Qt
from .qt.QtGui import QApplication
from .q_action_pipe import QActionPipe
from .q_deferred_caller import QDeferredCaller
from .qt_builder import QtBuilder
from .qt_object import QtObject


class QtApplication(Application):
    """ A concrete implementation of an Enaml application.

    A QtApplication uses the Qt toolkit to implement an Enaml UI that
    runs in the local process.

    """
    def __init__(self, factories, builder=None):
        """ Initialize a QtApplication.

        Parameters
        ----------
        factories : iterable
            An iterable of SessionFactory instances to pass to the
            superclass constructor.

        builder : QtBuilder or None
            An optional QtBuilder instance to manage the building of
            QtObject instances for this application. If not provided,
            a default builder will be used.

        """
        super(QtApplication, self).__init__(factories)
        self._qapp = QApplication.instance() or QApplication([])
        self._qcaller = QDeferredCaller()
        self._enaml_pipe = epipe = QActionPipe()
        self._qt_pipe = qpipe = QActionPipe()
        self._qt_builder = builder or QtBuilder()
        self._qt_objects = defaultdict(list)
        epipe.actionPosted.connect(self._on_enaml_action, Qt.QueuedConnection)
        qpipe.actionPosted.connect(self._on_qt_action, Qt.QueuedConnection)

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    @property
    def pipe_interface(self):
        """ Get the ActionPipeInterface for this application.

        Returns
        -------
        result : ActionPipeInterface
            An implementor of ActionPipeInterface which can be used by
            Enaml Object instances to send messages to their clients.

        """
        return self._enaml_pipe

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

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def start_session(self, name):
        """ Start a new session of the given name.

        This is an overridden parent class method which will build out
        the Qt client object tree for the session. It will be displayed
        when the application is started.

        """
        sid = super(QtApplication, self).start_session(name)
        pipe = self._qt_pipe
        builder = self._qt_builder
        objects = self._qt_objects[sid]
        for item in self.snapshot(sid):
            obj = builder.build(item, None, pipe)
            if obj is not None:
                obj.initialize()
                objects.append(obj)
        return sid

    def end_session(self, session_id):
        """ End the session with the given session id.

        This is an overridden parent class method which will removes
        the references to the Qt client object trees for the session.

        """
        super(QtApplication, self).end_session(session_id)
        self._qt_objects.pop(session_id, None)
        # XXX decide lifetime issues!
        # XXX this is the most reliable way to cleanup.
        import gc; gc.collect()

    def dispatch_qt_action(self, object_id, action, content):
        """ Dispatch an action to a qt object with the given id.

        This method can be called when a message from an Enaml widget
        is received and needs to be delivered to the Qt client widget.

        Parameters
        ----------
        object_id : str
            The unique identifier for the object.

        action : str
            The action to be performed by the object.

        content : dict
            The dictionary of content needed to perform the action.

        """
        obj = QtObject.lookup_object(object_id)
        if obj is None:
            # XXX disable for now to avoid annoying lifetime error
            # messages
            #print action, content
            #raise ValueError('Invalid object id')
            return
        obj.handle_action(action, content)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _on_enaml_action(self, object_id, action, content):
        """ Handle an action being posted by an Enaml object.

        """
        self.dispatch_qt_action(object_id, action, content)

    def _on_qt_action(self, object_id, action, content):
        """ Handle an action being posted by a Qt object.

        """
        self.dispatch_action(object_id, action, content)

