#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging

from enaml.application import Application

from .qt.QtCore import Qt
from .qt.QtGui import QApplication
from .q_action_pipe import QActionPipe
from .qt_factories import QT_FACTORIES
from .qt_object import QtObject


class QtApplication(Application):

    def __init__(self, factories, qt_factories=None):
        super(QtApplication, self).__init__(factories)
        self._qapp = QApplication.instance() or QApplication([])
        self._enaml_pipe = QActionPipe()
        self._qt_pipe = QActionPipe()
        self._qt_factories = qt_factories or QT_FACTORIES

        self._enaml_pipe.actionPosted.connect(self._on_enaml_message, Qt.QueuedConnection)
        self._qt_pipe.actionPosted.connect(self._on_qt_message, Qt.QueuedConnection)

    #--------------------------------------------------------------------------
    # Message Routing
    #--------------------------------------------------------------------------
    def _on_enaml_message(self, object_id, action, content):
        """ Handle an action being posted by an Enaml object.

        """
        self.dispatch_qt_object_message(object_id, action, content)

    def _on_qt_message(self, object_id, action, content):
        """ Handle an action being posted by a Qt object.

        """
        self.dispatch_object_message(object_id, action, content)

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    def pipe_interface(self):
        return self._enaml_pipe

    def start_session(self, name):
        sid = super(QtApplication, self).start_session(name)
        child_defs = [(-1, item) for item in self.snapshot(sid)]
        self._build_children(None, child_defs)
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
    def dispatch_qt_object_message(self, object_id, action, content):
        """ Dispatch a message to a qt object with the given id.

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
        if obj is not None:
            obj.handle_action(action, content)

    #--------------------------------------------------------------------------
    # Private API
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
                return widget_cls(tree_item['widget_id'], parent, self._qt_pipe)
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
        # The dict of factories to use for finding the right widget
        # class to use when building a widget.
        factories = self._qt_factories

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
    