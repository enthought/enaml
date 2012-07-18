#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.qt.qt.QtGui import QApplication
from enaml.qt.qt_factories import QT_FACTORIES
from enaml.qt.qt_hub import qt_message_hub
from enaml.qt.qt_registry import qt_register, qt_lookup
from enaml.qt.qt_zmq_client_worker import QtZMQClientWorker


class QtZMQApplication(object):
    """ An Enaml AsyncApplication which executes in the local process
    and uses Qt to create the client items.

    Since this is a locally running application, the Enaml messaging
    protocol is short-circuited in a few ways:
        1) No messages are serialized to json. The are transferred 
           between objects in their dictionary form since the 
           serialization step is entirely unnecessary.
        2) No messages are generated for the creation of widgets when
           they are published. The application just directly creates
           the widgets.

    """
    def __init__(self, factories=None):
        """ Initialize a QtLocalApplication.

        Parameters
        ----------
        factories : dict, optional
            An optional dictionary of qt widget factories to use when
            creating widgets.

        """
        # The internal Qt application object
        self._qapp = QApplication.instance() or QApplication([])
        if not hasattr(self._qapp, '_in_event_loop'):
            self._qapp._in_event_loop = False

        self._worker = QtZMQClientWorker('tcp://127.0.0.1', '6000', '6001')

        # The factories to use to create the Qt classes
        self._widget_factories = factories or QT_FACTORIES

        qt_register('app', self)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def receive(self, message):
        payload = message['payload']
        if payload['action'] == 'create':
            tree = payload['tree']
            self._create_view(tree)

    def _create_view(self, tree):
        new_widgets = []
        self._create(tree, new_widgets)
        
        # Run through the initializers for the new widgets.
        for widget, tree in new_widgets:
            widget.create()
        for widget, tree in new_widgets:
            widget.initialize(tree['attributes'])
        for widget, tree in new_widgets:
            widget.post_initialize()

    def _create(self, tree, new_widgets):
        factories = self._widget_factories

        target_id = tree['target_id']
        if qt_lookup(target_id):
            return

        widget_type = tree['type']
        if widget_type not in factories:
            # XXX what do we want to do here?
            print 'Unhandled widget type `%s`' % widget_type
            return

        parent = qt_lookup(tree['parent_id'])
        widget_cls = factories[widget_type]()
        widget = widget_cls(parent, target_id)
        qt_register(target_id, widget)

        new_widgets.append((widget, tree))
        
        for ctree in tree['children']:
            self._create(ctree, new_widgets)

    #--------------------------------------------------------------------------
    # App Interface
    #--------------------------------------------------------------------------
    def mainloop(self):
        """ Enter the mainloop of the application.

        This is a blocking call which starts and enters the main event 
        loop of the application. The event loop can be explicitly ended
        by calling the 'exit' method. The event loop can be implicitly
        terminated by closing all top-level windows. When the event 
        loop is exited, all existing Qt widgets will be discarded.

        """
        app = self._qapp
        if not getattr(app, '_in_event_loop', False):
            app._in_event_loop = True
            self._worker.daemon = True
            self._worker.start()
            message = {
                'type': 'message',
                'target_id': 'app',
                'operation_id': None,
                'payload': {
                    'action': 'create',
                    'name': 'main',
                }
            }
            qt_message_hub.post_message.emit(message)
            app.exec_()
            app._in_event_loop = False

    def exit(self):
        """ Exit the mainloop of the application.

        Calling this method will cause a previous blocking call to
        'mainloop' to unblock and return. If the mainloop is not 
        running, then this is a no-op.

        """
        app = self._qapp
        app.exit()
        app._in_event_loop = False


app = QtZMQApplication()
app.mainloop()

