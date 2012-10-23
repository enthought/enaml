#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import defaultdict
import logging

import wx

from enaml.application import Application

from .wx_action_pipe import wxActionPipe, EVT_ACTION_PIPE
from .wx_deferred_caller import wxDeferredCaller
from .wx_builder import WxBuilder
from .wx_object import WxObject


logger = logging.getLogger(__name__)


class WxApplication(Application):
    """ A concrete implementation of an Enaml application.

    A WxApplication uses the Wx toolkit to implement an Enaml UI that
    runs in the local process.

    """
    def __init__(self, factories, builder=None):
        """ Initialize a WxApplication.

        Parameters
        ----------
        factories : iterable
            An iterable of SessionFactory instances to pass to the
            superclass constructor.

        builder : WxBuilder or None
            An optional WxBuilder instance to manage the building of
            WxObject instances for this application. If not provided,
            a default builder will be used.

        """
        super(WxApplication, self).__init__(factories)
        self._wxapp = wx.GetApp() or wx.PySimpleApp()
        self._wxcaller = wxDeferredCaller()
        self._enaml_pipe = epipe = wxActionPipe()
        self._wx_pipe = wxpipe = wxActionPipe()
        self._wx_builder = builder or WxBuilder()
        self._wx_objects = defaultdict(list)
        epipe.Bind(EVT_ACTION_PIPE, self._on_enaml_action)
        wxpipe.Bind(EVT_ACTION_PIPE, self._on_wx_action)

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
        pipe = self._wx_pipe
        builder = self._wx_builder
        objects = self._wx_objects[sid]
        for item in self.snapshot(sid):
            obj = builder.build(item, None, pipe)
            if obj is not None:
                obj.initialize()
                objects.append(obj)
        return sid

    def end_session(self, session_id):
        """ End the session with the given session id.

        This is an overridden parent class method which will removes
        the references to the Wx client object trees for the session.

        """
        super(WxApplication, self).end_session(session_id)
        self._wx_objects.pop(session_id, None)
        # XXX decide lifetime issues!
        # XXX this is the most reliable way to cleanup.
        import gc; gc.collect()

    def dispatch_wx_action(self, object_id, action, content):
        """ Dispatch an action to a wx object with the given id.

        This method can be called when a message from an Enaml widget
        is received and needs to be delivered to the Wx client widget.

        Parameters
        ----------
        object_id : str
            The unique identifier for the object.

        action : str
            The action to be performed by the object.

        content : dict
            The dictionary of content needed to perform the action.

        """
        obj = WxObject.lookup_object(object_id)
        if obj is None:
            msg = "Invalid object id sent to WxApplication: %s:%s"
            logger.warn(msg % (object_id, action))
            return
        obj.handle_action(action, content)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _on_enaml_action(self, event):
        """ Handle an action event being posted by an Enaml object.

        """
        object_id = event.object_id
        action = event.action
        content = event.content
        self.dispatch_wx_action(object_id, action, content)

    def _on_wx_action(self, event):
        """ Handle an action event being posted by a Wx object.

        """
        object_id = event.object_id
        action = event.action
        content = event.content
        self.dispatch_action(object_id, action, content)

