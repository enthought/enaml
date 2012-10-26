#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from collections import defaultdict
from concurrent import futures
import logging

from enaml.application import Application
from enaml.core.object import ActionPipeInterface
from enaml.signaling import Signal

from .mock_widget import MockWidget

logger = logging.getLogger(__name__)

def mock_factory():
    return MockWidget


MOCK_FACTORIES = {
    'Action': mock_factory,
    'ActionGroup': mock_factory,
    'Calendar': mock_factory,
    'CheckBox': mock_factory,
    'ComboBox': mock_factory,
    'Container': mock_factory,
    'DateSelector': mock_factory,
    'DatetimeSelector': mock_factory,
    'DockPane': mock_factory,
    'Field': mock_factory,
    'Form': mock_factory,
    'GroupBox': mock_factory,
    'Html': mock_factory,
    'ImageView': mock_factory,
    'Label': mock_factory,
    'MainWindow': mock_factory,
    'MdiArea': mock_factory,
    'MdiWindow': mock_factory,
    'Menu': mock_factory,
    'MenuBar': mock_factory,
    'Notebook': mock_factory,
    'Page': mock_factory,
    'PushButton': mock_factory,
    'ProgressBar': mock_factory,
    'RadioButton': mock_factory,
    'ScrollArea': mock_factory,
    'Slider': mock_factory,
    'SpinBox': mock_factory,
    'Splitter': mock_factory,
    'Stack': mock_factory,
    'StackItem': mock_factory,
    'TextEditor': mock_factory,
    'ToolBar': mock_factory,
    'Window': mock_factory,
    'WidgetComponent': mock_factory,
}


class MockActionPipe(object):
    """ A messaging pipe implementation.

    This is a mock pipe class which converts a `send` on the pipe
    into a signal which is connected to by the MockApplication.

    This object also satisfies the Enaml ActionPipeInterface.

    """
    #: A signal emitted when an item has been sent down the pipe.
    actionPosted = Signal()

    def send(self, object_id, action, content):
        """ Send the action to any attached listeners.

        Parameters
        ----------
        object_id : str
            The object id of the target object.

        action : str
            The action that should be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        logger.debug('Sending %s %s %s', object_id, action, content)
        self.actionPosted.emit(object_id, action, content)


ActionPipeInterface.register(MockActionPipe)



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
        if class_name in factories:
            obj_cls = factories[class_name]()
        else:
            obj_cls = None
            for base in tree['bases']:
                if base in factories:
                    obj_cls = factories[base]()
                    break
        if obj_cls is None:
            msg =  'Unhandled object type: %s:%s'
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

        self._enaml_pipe = epipe = MockActionPipe()
        self._builder = MockBuilder()
        self._objects = defaultdict(list)

        epipe.actionPosted.connect(self.dispatch_action)

    @property
    def pipe_interface(self):
        return self._enaml_pipe

    def start(self):
        self._executor = futures.ThreadPoolExecutor(max_workers=1)

    def stop(self):
        self._objects.clear()
        self._executor.shutdown()

    def deferred_call(self, callback, *args, **kwargs):
        # Execute this asynchronously
        logger.debug('Deferred call to %s', callback)
        self._executor.submit(callback, *args, **kwargs)

    def timed_call(self, ms, callback, *args, **kwargs):
        # This function is currently unused in the code base. 
        raise NotImplementedError

    def start_session(self, name):
        """ Start a new session of the given name.

        This is an overridden parent class method which will build out
        the Qt client object tree for the session. It will be displayed
        when the application is started.

        """
        sid = super(MockApplication, self).start_session(name)
        pipe = self._enaml_pipe
        builder = self._builder
        objects = self._objects[sid]
        for item in self.snapshot(sid):
            obj = builder.build(item, None, pipe)
            if obj is not None:
                objects.append(obj)
        return sid

    def dispatch_action(self, object_id, action, content):
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

