#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.messaging import hub
from enaml.messaging import registry

from .qt.QtGui import QApplication
from .qt_factories import QT_FACTORIES
from .qt_hub import qt_message_hub
from .qt_registry import qt_register, qt_lookup


class QtLocalApplication(object):
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
        # The internal Qt application object
        self._qapp = QApplication.instance() or QApplication([])
        if not hasattr(self._qapp, '_in_event_loop'):
            self._qapp._in_event_loop = False

        # The factories to use to create the Qt classes
        self._widget_factories = factories or QT_FACTORIES

        self._views = {}

        qt_message_hub.post_message.connect(self._on_qt_posted_message)
        hub.connect(self._on_posted_message)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _on_qt_posted_message(self, message):
        target_id = message['target_id']
        receiver = registry.lookup(target_id)
        if receiver is not None:
            receiver.receive(message)

    def _on_posted_message(self, message):
        qt_message_hub.deliver_message.emit(message)

    def _create_views(self):
        for view in self._views.values():
            tree = view.creation_tree()

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
    # AsyncApplication Interface
    #--------------------------------------------------------------------------
    def serve(self, name, view):
        self._views[name] = view

    def mainloop(self):
        app = self._qapp
        if not getattr(app, '_in_event_loop', False):
            app._in_event_loop = True
            self._create_views()
            app.exec_()
            app._in_event_loop = False

    def exit(self):
        app = self._qapp
        app.exit()
        app._in_event_loop = False

