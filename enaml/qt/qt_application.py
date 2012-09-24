#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.application import Application

from .qt.QtCore import Qt
from .qt.QtGui import QApplication
from .q_action_pipe import QActionPipe
from .qt_factories import QT_FACTORIES
from .qt_object import QtObject


class QtApplication(Application):
    """ A concrete implementation of an Enaml application. 

    A QtApplication uses the Qt4 toolkit to implement an Enaml UI that
    runs in the local process.

    """
    def __init__(self, factories, qt_factories=None):
        """ Initialize a QtApplication.

        Parameters
        ----------
        factories : iterable
            An iterable of SessionFactory instances to pass to the
            superclass constructor.

        """
        super(QtApplication, self).__init__(factories)
        self._qapp = QApplication.instance() or QApplication([])
        self._enaml_pipe = QActionPipe()
        self._qt_pipe = QActionPipe()
        self._qt_factories = qt_factories or QT_FACTORIES
        self._qt_objects = []

        conn = Qt.QueuedConnection
        self._enaml_pipe.actionPosted.connect(self._on_enaml_action, conn)
        self._qt_pipe.actionPosted.connect(self._on_qt_action, conn)

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def pipe_interface(self):
        return self._enaml_pipe

    def start_session(self, name):
        sid = super(QtApplication, self).start_session(name)
        factories = self._qt_factories
        for item in self.snapshot(sid):
            for base in item['bases']:
                if base in factories:
                    object_cls = factories[base]()
                    obj = object_cls.build(None, item, self._qt_pipe, factories)
                    self._qt_objects.append(obj)
                    break
        return sid

    def start(self):
        """ Start the sever's main loop.

        This will enter the main GUI event loop and block until a call
        to 'stop' is made, at which point this method will return.

        """
        app = self._qapp
        if not getattr(app, '_in_event_loop', False):
            app._in_event_loop = True
            app.exec_()
            app._in_event_loop = False

    def stop(self):
        """ Stop the server's main loop.

        Calling this method will cause a previous call to 'start' to 
        unblock and return.

        """
        app = self._qapp
        app.exit()
        app._in_event_loop = False

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
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
            raise ValueError('Invalid object id')
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

    