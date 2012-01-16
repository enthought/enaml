#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from ..abstract_application import AbstractTkApplication


class WXApplication(AbstractTkApplication):
    """ A Wx implementation of AbstractTkApplication.

    """
    def initialize(self, *args, **kwargs):
        """ Initializes the underlying wxApp object. It does *not* 
        start the event loop. If the application object is already 
        created, it is a no-op.

        """     
        app = wx.GetApp()
        if app is None:
            app = wx.PySimpleApp(*args, **kwargs)
        self._wx_app = app

    def start_event_loop(self):
        """ Starts the underlying application object's event loop, or 
        does nothing if it is already started. A RuntimeError will be 
        raised if the application object is not yet created.

        """
        app = wx.GetApp()
        if app is None:
            msg = 'Cannot start event loop. Application object not created.'
            raise RuntimeError(msg)
        
        if not app.IsMainLoopRunning():
            app.MainLoop()
                
    def event_loop_running(self):
        """ Returns True if the main event loop is running, False 
        otherwise.

        """
        app = wx.GetApp()
        if app is None:
            return False
        return app.IsMainLoopRunning()

    def app_object(self):
        """ Returns the underlying application object, or None if one 
        does not exist.

        """
        return wx.GetApp()

    def is_main_thread(self):
        """ Return True if this method was called from the main event
        thread, False otherwise.

        """
        app = wx.GetApp()
        if app is None:
            raise RuntimeError('Application object not yet created')
        return wx.Thread_IsMain()

    def call_on_main(self, callback, *args, **kwargs):
        """ Invoke the given callable in the main gui event thread at 
        some point in the future.

        Parameters
        ----------
        callback : callable
            The callable object to execute at some point in the future.

        *args
            Any positional arguments to pass to the callback.

        **kwargs
            Any keyword arguments to pass to the callback.

        """
        wx.CallAfter(callback, *args, **kwargs)

    def timer(self, ms, callback, *args, **kwargs):
        """ Invoke the given callable in the main gui event thread at 
        the given number of milliseconds in the future.

        Parameters
        ----------
        ms : int
            The number of milliseconds in the future to invoke the
            callable.

        callback : callable
            The callable object to execute at some point in the future.

        *args
            Any positional arguments to pass to the callback.

        **kwargs
            Any keyword arguments to pass to the callback.

        """
        wx.CallLater(ms, callback, *args, **kwargs)

    def process_events(self):
        """ Process all of the pending events in the event queue.

        """
        wx.YieldIfNeeded()

