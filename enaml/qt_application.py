#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging
from enaml.core.object import Object

from .qt.qt.QtCore import QTimer, Signal, QObject, Qt
from .qt.qt.QtGui import QApplication
from .qt.qt_factories import QT_FACTORIES

from .core_application import CoreApplication


class QCallbackRunner(QObject):

    callbackPosted = Signal(object)

    def __init__(self):
        super(QCallbackRunner, self).__init__()
        self.callbackPosted.connect(self.onCallbackPosted, Qt.QueuedConnection)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def onCallbackPosted(self, item):
        callback, args, kwargs = item
        callback(*args, **kwargs)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def postCallback(self, callback, args, kwargs):
        item = (callback, args, kwargs)
        self.callbackPosted.emit(item)

    def timedCallback(self, ms, callback, args, kwargs):
        fn = lambda: callback(*args, **kwargs)
        item = (QTimer.singleShot, (ms, fn), {})
        self.callbackPosted.emit(item)


class QtApplication(CoreApplication):

    def __init__(self, objects=None, factories=None):
        super(QtApplication, self).__init__(objects)
        self._qapp = QApplication.instance() or QApplication([])
        self._cbrunner = QCallbackRunner()
        self._widgets = {}
        self._factories = factories or QT_FACTORIES

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    def call_on_main(self, callback, *args, **kwargs):
        """

        """
        self._cbrunner.postCallback(callback, args, kwargs)

    def timer(self, ms, callback, *args, **kwargs):
        """

        """
        self._cbrunner.timedCallback(ms, callback, args, kwargs)
    
    def process_events(self):
        """

        """
        self._qapp.processEvents()

    def start(self):
        """

        """
        app = self._qapp
        if not getattr(app, '_in_event_loop', False):
            app._in_event_loop = True
            child_defs = [(-1, item) for item in self.snapshot()]
            self._build_children(None, child_defs)
            app.exec_()
            app._in_event_loop = False

    def stop(self):
        """

        """
        app = self._qapp
        app.exit()
        app._in_event_loop = False

    #--------------------------------------------------------------------------
    # Building
    #--------------------------------------------------------------------------
    def _build_widget(self, parent, tree_item, factories):
        """ A private method which constructs the given widget.

        Parameters
        ----------
        parent : QtMessengerWidget or None
            The widget to use a parent for the widget being built.

        tree_item : dict
            The dictionary representing the UI tree for the widget.
            Only the root level widget will be built.

        factories : dict
            The dict of factories to use for building the widget.

        Returns
        -------
        result : QtMessengerWidget or None
            The built widget, or None if the widget could not be built.
            A failed build will be logged as an error. The returned
            widget is *not* added to the parent. That responsibility
            lies with the caller.

        """
        # Walk along the types mro to see if we have a factory
        # that can handle the widget type. The 'class' of the
        # tree item is also the first item in 'bases', so there
        # is no need to test it separately.
        for base in tree_item['bases']:
            if base in factories:
                widget_cls = factories[base]()
                return widget_cls(parent, tree_item['widget_id'], self)
        else:
            # XXX what do we really want to do here? 
            msg =  'Unhandled widget type: %s:%s'
            item_class = tree_item['class']
            item_bases = tree_item['bases']
            logging.error(msg % (item_class, item_bases))
        
    def _build_children(self, parent, child_defs):
        """ A private method which builds the children of a parent.

        Parameters
        ----------
        parent : QtMessengerWidget or None
            The messenger widget to use as the parent of the widgets
            being created, or None if they have no parent.

        child_defs : list of tuples
            A list of the form (index, snapshot) where index is the
            integer index to use when inserting the newly built child
            into the parent. If the index is -1, the child will be 
            simply added to the parent. The 'snapshot' is the dict
            representing the ui tree to build for the child. 

        """
        # The dict of widget_id -> widget used for message dispatching
        widgets = self._widgets

        # The dict of factories to use for finding the right widget
        # class to use when building a widget.
        factories = self._factories

        # The flat list of widgets created during this build pass. The
        # widgets are collected so that the initialization passes can
        # be performed without traversing the tree. 
        created = []

        # Pre-fetch the bound method for actually building a widget.
        build = self._build_widget

        # A stack used for pushing tree items and their index
        tree_stack = []
        tree_push = tree_stack.append
        tree_pop = tree_stack.pop

        # A stack used pushing parent items
        parent_stack = []
        parent_push = parent_stack.append
        parent_pop = parent_stack.pop

        # This loop recursively builds out the trees, starting with 
        # parents and moving to children. Toplevel tree components 
        # are expected to take None as a parent.
        for index, tree in child_defs:
            tree_push((index, tree))
            parent_push(parent)
            while tree_stack:
                tree_index, tree_item = tree_pop() 
                parent = parent_pop()
                widget = build(parent, tree_item, factories)
                if widget is None:
                    # widget build failed; logged to error
                    continue
                if parent is not None:
                    if tree_index == -1:
                        parent.add_child(widget)
                    else:
                        parent.insert_child(tree_index, widget)
                widgets[widget.widget_id()] = widget
                created.append((widget, tree_item))
                for child_tree in reversed(tree_item['children']):
                    tree_push((-1, child_tree))
                    parent_push(widget)

        # Create and initialize the widgets top-down
        for widget, tree in created:
            widget.create(tree)

        # Run the layout initialization bottom-up
        for widget, tree in reversed(created):
            widget.init_layout()

    def send_action(self, object_id, action, content):
        obj = Object.lookup_object(object_id)
        if obj is not None:
            obj.handle_action(action, content)

    def handle_action(self, object_id, action, content):
        obj = self._widgets.get(object_id)
        if obj is not None:
            obj.handle_action(action, content)

