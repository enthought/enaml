#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import deque
from threading import Lock

from .qt.QtCore import  Qt, QObject, QTimer, QThread, Slot, QMetaObject
from .qt.QtGui import QApplication

from ..abstract_application import AbstractTkApplication


class DeferredCaller(QObject):
    """ A QObject subclass that will invoke a callable on the main
    gui event thread. The only public api is the enqueue classmethod.

    """
    #: The private internal queue of pending tasks.
    _queue = deque()

    #: The private threading Lock which protects access to the queue 
    #: and creation of the internal singleton instance.
    _lock = Lock()

    @classmethod
    def enqueue(cls, callback, *args, **kwargs):
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
        try:
            instance = cls._instance
        except AttributeError:
            with cls._lock:
                try:
                    instance = cls._instance
                except AttributeError:
                    instance = cls._instance = cls()
        instance._enqueue(callback, args, kwargs)

    def __init__(self):
        super(DeferredCaller, self).__init__()
        # Move the object to the main thread so that all signal/slot 
        # connections invoke the slots on the main thread. This call
        # is required since there is potential for this object to be
        # created from a non-gui thread.
        self.moveToThread(QApplication.instance().thread())

    def _enqueue(self, callback, args, kwargs):
        """ A private method which places the callback, args, and kwargs
        into the internal queue and and invokes the dispatch method on 
        the main thread.

        """
        item = (callback, args, kwargs)
        with self._lock:
            self._queue.append(item)
        # Invoking the method via QMetaObject with a QueuedConnection
        # has seemed to be the most reliable way of executing something
        # on the main thread. Other attempts with using QEvents under
        # heavy load have resulted in dropped (maybe compressed?)
        # events which leads to hard to trace bugs when application
        # code is relying on callbacks to be executed.
        QMetaObject.invokeMethod(self, '_dispatch', Qt.QueuedConnection)

    @Slot()
    def _dispatch(self):
        """ A private method which runs the next task in the queue. This
        method is a qt slot and is invoked from the main gui thread via
        QMetaObject.invokMethod.
        
        """ 
        queue = self._queue
        with self._lock:
            if not queue:
                return
            callback, args, kwargs = queue.popleft()
        callback(*args, **kwargs)


class QtApplication(AbstractTkApplication):
    """ A Qt4 implementation of AbstractTkApplication.

    """
    def initialize(self, *args, **kwargs):
        """ Initializes the underlying QApplication object. It does 
        *not* start the event loop. If the application object is already
        created, it is a no-op.

        """     
        app = QApplication.instance()
        if app is None:
            if not args:
                args = ([''],)
            app = QApplication(*args, **kwargs)   
        self._qt_app = app
    
    def start_event_loop(self):
        """ Starts the underlying application object's event loop, or 
        does nothing if it is already started. A RuntimeError will be 
        raised if the application object is not yet created.

        """
        app = QApplication.instance()
        if app is None:
            msg = 'Cannot start event loop. Application object not created.'
            raise RuntimeError(msg)
        
        if not getattr(app, '_in_event_loop', False):
            app._in_event_loop = True
            app.exec_()
            app._in_event_loop = False
    
    def event_loop_running(self):
        """ Returns True if the main event loop is running, False 
        otherwise.

        """
        app = QApplication.instance()
        return getattr(app, '_in_event_loop', False)

    def app_object(self):
        """ Returns the underlying application object, or None if one 
        does not exist.

        """
        return QApplication.instance()

    def is_main_thread(self):
        """ Return True if this method was called from the main event
        thread, False otherwise.

        """
        app = QApplication.instance()
        if app is None:
            raise RuntimeError('Application object not yet created')
        return app.thread() == QThread.currentThread()

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
        DeferredCaller.enqueue(callback, *args, **kwargs)

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
        fn = lambda: callback(*args, **kwargs)
        DeferredCaller.enqueue(QTimer.singleShot, ms, fn)

    def process_events(self):
        """ Process all of the pending events in the event queue.

        """
        QApplication.instance().processEvents()

