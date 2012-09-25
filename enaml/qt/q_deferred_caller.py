#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import QObject, QTimer, Qt, Signal
from .qt.QtGui import QApplication


class QDeferredCaller(QObject):
    """ A QObject subclass which facilitates executing callbacks on the
    main application thread.

    """
    _posted = Signal(object)

    def __init__(self):
        """ Initialize a QDeferredCaller.

        """
        super(QDeferredCaller, self).__init__()
        app = QApplication.instance()
        if app is not None:
            self.moveToThread(app.thread())
        self._posted.connect(self._onPosted, Qt.QueuedConnection)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _onPosted(self, callback):
        """ A private signal handler for the '_callbackPosted' signal.

        This handler simply executes the callback.

        """
        callback()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def deferredCall(self, callback, *args, **kwargs):
        """ Execute the callback on the main gui thread.

        Parameters
        ----------
        callback : callable
            The callable object to execute on the main thread.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to 
            the callback.

        """
        f = lambda: callback(*args, **kwargs)
        self._posted.emit(f)

    def timedCall(self, ms, callback, *args, **kwargs):
        """ Execute a callback on timer in the main gui thread.

        Parameters
        ----------
        ms : int
            The time to delay, in milliseconds, before executing the
            callable.
            
        callback : callable
            The callable object to execute at on the timer.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to 
            the callback.

        """
        f = lambda: callback(*args, **kwargs)
        f2 = lambda: QTimer.singleShot(ms, f)
        self._posted.emit(f2)

