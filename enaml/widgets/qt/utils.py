""" Qt-specific utilities.
"""

from .qt import QtCore, QtGui


class _FutureCall(QtCore.QObject):
    """ This is a helper class that is similar to the wx FutureCall class. """

    # Keep a list of references so that they don't get garbage collected.
    _calls = []

    # Manage access to the list of instances.
    _calls_mutex = QtCore.QMutex()

    # A new Qt event type for _FutureCalls
    _pyface_event = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    def __init__(self, ms, callable, *args, **kw):
        super(_FutureCall, self).__init__()

        # Save the arguments.
        self._ms = ms
        self._callable = callable
        self._args = args
        self._kw = kw

        # Save the instance.
        self._calls_mutex.lock()
        self._calls.append(self)
        self._calls_mutex.unlock()

        # Move to the main GUI thread.
        #self.moveToThread(QtGui.QApplication.instance().thread())

        # Post an event to be dispatched on the main GUI thread. Note that
        # we do not call QTimer.singleShot here, which would be simpler, because
        # that only works on QThreads. We want regular Python threads to work.
        event = QtCore.QEvent(self._pyface_event)
        QtGui.QApplication.postEvent(self, event)
        QtGui.QApplication.sendPostedEvents()

    def event(self, event):
        """ QObject event handler.
        """
        if event.type() == self._pyface_event:
            # Invoke the callable
            if self._ms:
                QtCore.QTimer.singleShot(self._ms, self._dispatch)
            else:
                self._callable(*self._args, **self._kw)
                # We cannot remove from self._calls here. QObjects don't like
                # being garbage collected during event handlers.
                QtCore.QTimer.singleShot(0, self._finished)
            return True

        return super(_FutureCall, self).event(event)

    def _dispatch(self):
        """ Invoke the callable.
        """
        try:
            self._callable(*self._args, **self._kw)
        finally:
            self._finished()

    def _finished(self):
        """ Remove the call from the list, so it can be garbage collected.
        """
        self._calls_mutex.lock()
        try:
            self._calls.remove(self)
        finally:
            self._calls_mutex.unlock()

def invoke_later(callable, *args, **kwds):
    """ Invoke a function later in the event loop.

    """
    _FutureCall(0, callable, *args, **kwds)

