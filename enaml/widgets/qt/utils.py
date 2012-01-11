#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" Qt-specific utilities.

"""
from .qt.QtCore import QMutex, QEvent, QObject, QTimer
from .qt.QtGui import QApplication


class _FutureCall(QObject):
    """ This is a helper class that is similar to the wx FutureCall class. 
    
    """
    # Keep a list of instances so that they don't get garbage collected.
    _calls = []

    # Manage access to the list of instances.
    _calls_mutex = QMutex()

    # A new Qt event type for _FutureCalls
    _call_event = QEvent.Type(QEvent.registerEventType())

    def __init__(self, ms, callable, *args, **kw):
        super(_FutureCall, self).__init__()
        self._ms = ms
        self._callable = callable
        self._args = args
        self._kw = kw

        # Save the instance while protecting access to the list 
        # since there may be multiple threads using invoke_later.
        mutex = self._calls_mutex
        mutex.lock()
        self._calls.append(self)
        mutex.unlock()

        # Move to the main GUI thread in order to post the event.
        self.moveToThread(QApplication.instance().thread())

        # Post an event to be dispatched on the main GUI thread. Note 
        # that we do not call QTimer.singleShot here, which would be 
        # simpler, because that only works on QThreads. We want regular 
        # Python threads to work.
        event = QEvent(self._call_event)
        QApplication.postEvent(self, event)

    def event(self, event):
        """ QObject event handler. Dispatches to the callable immediately
        or via a Timer if the callable should happen some milliseconds
        later.

        """
        # This must be '==', 'is' does not work here.
        if event.type() == self._call_event:
            if self._ms > 0:
                QTimer.singleShot(self._ms, self._dispatch)
            else:
                self._dispatch()
            return True

        return super(_FutureCall, self).event(event)

    def _dispatch(self):
        """ Invokes the callable and removes the instance from the
        list of calls so that it can be garbage collected.

        """
        try:
            self._callable(*self._args, **self._kw)
        finally:
            mutex = self._calls_mutex
            mutex.lock()
            try:
                self._calls.remove(self)
            finally:
                mutex.unlock()


def invoke_later(callable, *args, **kwds):
    """ Invoke a function at some point later in the event loop.

    """
    _FutureCall(0, callable, *args, **kwds)
    

def invoke_timer(ms, callable, *args, **kwds):
    """ Invoke a function some milliseconds from now.

    """
    _FutureCall(ms, callable, *args, **kwds)

