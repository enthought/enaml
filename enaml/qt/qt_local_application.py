#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from itertools import count

from enaml.async.async_application import AsyncApplication

from .qt.QtCore import Qt
from .qt.QtGui import QApplication
from .qt_clients import CLIENTS
from .qt_local_pipe import QtLocalPipe


def local_id_gen(stem):
    """ An identifier generator used by the QtLocalApplication to 
    generate unique identifiers for messaging.

    Parameters
    ----------
    stem : str
        A string stem to prepend to a incrementing integer value.

    """
    counter = count()
    str_ = str
    while True:
        yield stem + str_(counter.next())


class QtLocalApplication(AsyncApplication):
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

        # The target id generator which will yield unique target
        # identifiers for the async messengers during registration
        self._target_id_gen = local_id_gen('w')

        # An mapping of the messengers which registered themselves 
        # by calling the .register method.
        self._messengers = {}

        # A mapping of target ids to the created qt widgets when
        # they get published.
        self._widgets = {}

        # The operation identifier generator which will create unique
        # ids for request operations. The same generator is used for 
        # both so that there is no chance of having duplicate ids.
        op_id_gen = local_id_gen('op')

        # The pipe used by the messengers for communicating
        self._messenger_pipe = server = QtLocalPipe(op_id_gen)

        # The pipe used by the qt widgets for communicating
        self._widget_pipe = client = QtLocalPipe(op_id_gen)

        # The factories to use to create the Qt classes
        self._widget_factories = factories or CLIENTS

        # Hook up the signals and slots on the two pipes to enable
        # queued message passing between them.
        conn = Qt.QueuedConnection
        server.send_operation.connect(client.receive_operation, conn)
        client.send_operation.connect(server.receive_operation, conn)

    #--------------------------------------------------------------------------
    # AsyncApplication Interface
    #--------------------------------------------------------------------------
    def register(self, messenger):
        """ Register a messenger with the application.

        This will assign the messenger a target id and an async pipe
        to use for communication. The target id will be assigned before
        the pipe, since the property setter for the pipe may depend on
        the existence of the target id.

        It is assumed that any given messenger will only be registered 
        once. No checks are made to prevent multiple registrations.

        Parameters
        ----------
        messenger : AsyncMessenger
            An async messenger instance which should be registered with
            the application.

        """
        target_id = self._target_id_gen.next()
        messenger.target_id = target_id
        messenger.async_pipe = self._messenger_pipe
        self._messengers[target_id] = messenger

    def publish(self, targets):
        """ Make previously registered messengers available on the 
        client.

        If the application is not yet running, the targets will be
        published as the mainloop of the application is started. If
        the application is already running, the targets will be 
        published immediately.

        Parameters
        ----------
        targets : iterable
            An iterable which yields the target ids for previously 
            registered AsyncMessenger instances. If any of the target
            ids do not exist, or were not registered, a ValueError will
            be raised and nothing will be transmitted to the client.

        """
        messengers = self._messengers
        widgets = self._widgets
        not_yet_created = []
        for target in targets:
            if target not in messengers:
                raise ValueError('Unregistered target `%s`' % target)
            if target not in widgets:
                not_yet_created.append(target)
        self._create(not_yet_created)

    def destroy(self, targets):
        """ Destroy previously registered messengers. If the messenger
        has been published, it will be effecitvely unpublished.

        Parameters
        ----------
        targets : iterable
            An iterable which yields the target ids for previously 
            registered AsyncMessenger instances. If any of the target
            ids do not exist, or were not registered, that id will
            be skipped.

        """
        widgets = self._widgets
        for target in targets:
            widget = widgets.pop(target, None)
            if widget is not None:
                widget.destroy()

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
            app.exec_()
            app._in_event_loop = False
            self._widgets.clear()

    def exit(self):
        """ Exit the mainloop of the application.

        Calling this method will cause a previous blocking call to
        'mainloop' to unblock and return. If the mainloop is not 
        running, then this is a no-op.

        """
        app = self._qapp
        app.exit()
        app._in_event_loop = False

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _create_widget(self, target, payloads):
        """ A private method which will create the widget for the given
        target id, recursively creating the parent if necessary.

        If a target has a parent id which does not yet have a widget or
        is an id which is not included in the payloads, and therefore
        cannot have a parent created, None will be used.

        Parameters
        ----------
        target : str
            The target id for the widget to create.

        payloads : dict
            A dict mapping target ids to widgets which have not yet
            been created.

        """
        payload = payloads[target]
        widget_type = payload['type']
        factories = self._widget_factories
        if widget_type not in factories:
            # XXX what do we want to do here?
            print 'Unhandled widget type `%s`' % widget_type
            return

        widgets = self._widgets
        parent_id = payload['parent_id']
        if parent_id is not None:
            if parent_id not in self._widgets:
                if parent_id not in payloads:
                    # XXX want do we want to do here? For now just
                    # print the error have None be used as the parent.
                    msg = 'Could not create parent widget `%s`'
                    print msg % parent_id
                else:
                    self._create_widget(parent_id, payloads)

        parent = widgets.get(parent_id)
        widget_cls = factories[widget_type]()
        widget = widget_cls(parent, target, self._widget_pipe)
        widgets[target] = widget
        return widget

    def _create(self, targets):
        """ Create the widgets for the specified target ids.

        It is assumed that the widgets for the given target ids do not
        already exist. If a factory does not exist for a certain widget,
        then the default widget will be used in its place.

        Parameters
        ----------
        targets : list
            A list of target id strings of messengers which should have
            widgets created for them.

        """
        # XXX we don't yet have the concept of a default widget. We
        # probably want to do something like a label with bold centered
        # text displaying an error message saying that widget factory
        # doesn't exist. Perhaps...

        # Create a mapping between the target id's and their creation
        # payloads. This allows us to efficiently create the widgets 
        # in order, creating the parents along the way if necessary.
        msgrs = self._messengers
        payloads = {}
        for target in targets:
            payloads[target] = msgrs[target].creation_payload()

        # Create the new widgets, recursively creating parents if that
        # is necessary.
        new_widgets = []
        create_widget = self._create_widget
        for target in targets:
            widget = create_widget(target, payloads)
            new_widgets.append((target, widget))

        # Run through the initializers for the new widgets.
        for target, widget in new_widgets:
            widget.create()
        for target, widget in new_widgets:
            payload = payloads[target]
            widget.initialize(payload['attributes'])
        for target, widget in new_widgets:
            widget.post_initialize()

