#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from collections import defaultdict
import logging

from enaml.application import Application
from enaml.qt.q_action_pipe import QActionPipe
from enaml.qt.q_deferred_caller import QDeferredCaller
from enaml.qt.qt_factories import QT_FACTORIES

from .mock_widget import MockWidget

logger = logging.getLogger(__name__)


def mock_factory():
    return MockWidget

# Generate the MOCK_FACTORIES dictionnary based on the QT_FACTORIES
MOCK_FACTORIES = {key: mock_factory for key in QT_FACTORIES}
MOCK_FACTORIES['WidgetComponent'] = mock_factory



class MockBuilder(object):
    """ An object which manages building a QtObject tree from an Enaml
    snapshot dict.

    """
    def __init__(self, factories=None):
        """ Initialize a QtBuilder.

        Parameters
        ----------
        factories : dict or None
            A dictionary mapping an Enaml class name to function which
            will import and return the appropriate QtObject subclass.
            If None is provied, the default QT_FACTORIES dict will be
            used.

        """
        self._factories = factories or MOCK_FACTORIES

    def build(self, tree, parent, pipe):
        """ Build the Qt object tree for the given Enaml tree.

        Parameters
        ----------
        tree : dict
            An Enaml snapshot tree representing an object dict.

        parent : QtObject or None
            The parent for the tree, or None if the tree is top-level.

        pipe : QActionPipe
            The action pipe to pass to new QtObject instances.

        """

        factories = self._factories
        class_name = tree['class']
        obj_cls = mock_factory()
        if class_name in factories:
            obj_cls = factories[class_name]()
        else:
            obj_cls = None
            for base in tree['bases']:
                if base in factories:
                    obj_cls = factories[base]()
                    break
        if obj_cls is None:
            msg = 'Unhandled object type: %s:%s'
            item_class = tree['class']
            item_bases = tree['bases']
            logger.error(msg % (item_class, item_bases))
            return
        obj = obj_cls.construct(tree, parent, pipe, self)
        for child in tree['children']:
            self.build(child, obj, pipe)
        return obj

class MockApplication(Application):

    def __init__(self, factories):

        super(MockApplication, self).__init__(factories)

        self._enaml_pipe = epipe = QActionPipe()
        self._toolkit_pipe = tpipe = QActionPipe()
        self._qcaller = QDeferredCaller()

        self._builder = MockBuilder()
        self._toolkit_objects = defaultdict(list)

        epipe.actionPosted.connect(self._on_enaml_action)
        tpipe.actionPosted.connect(self._on_toolkit_action)

    @property
    def pipe_interface(self):
        return self._enaml_pipe

    def start(self):
        pass

    def stop(self):
        self._toolkit_objects.clear()

    def deferred_call(self, callback, *args, **kwargs):
        # Execute this asynchronously
        logger.debug('Deferred call to %s', callback)
        self._qcaller.deferredCall(callback, *args, **kwargs)

    def timed_call(self, ms, callback, *args, **kwargs):
        # This function is currently unused in the code base.
        raise NotImplementedError

    def start_session(self, name):
        """ Start a new session of the given name.

        This is an overridden parent class method which will build out
        the mock client object tree for the session. It will be displayed
        when the application is started.

        """
        sid = super(MockApplication, self).start_session(name)
        pipe = self._toolkit_pipe
        builder = self._builder
        objects = self._toolkit_objects[sid]
        for item in self.snapshot(sid):
            obj = builder.build(item, None, pipe)
            if obj is not None:
                objects.append(obj)
        return sid

    def dispatch_toolkit_action(self, object_id, action, content):
        """ Dispatch an action to an object with the given id.

        This method can be called by subclasses when they receive an
        action message from a client object. If the object does not
        exist, an exception will be raised.

        Parameters
        ----------
        object_id : str
            The unique identifier for the object.

        action : str
            The action to be performed by the object.

        content : dict
            The dictionary of content needed to perform the action.

        """
        logger.debug('Dispatching action %s %s %s', object_id, action, content)
        obj = MockWidget.lookup_object(object_id)
        if obj is None:
            raise ValueError('Invalid object id')
        obj.handle_action(action, content)


    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _on_enaml_action(self, object_id, action, content):
        """ Handle an action being posted by an Enaml object.

        """
        self.dispatch_toolkit_action(object_id, action, content)

    def _on_toolkit_action(self, object_id, action, content):
        """ Handle an action being posted by a Mock object.

        """
        self.dispatch_action(object_id, action, content)

### EOF
