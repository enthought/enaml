#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging
from weakref import WeakValueDictionary

from enaml.utils import LoopbackGuard


class QtObject(object):
    """ The most base class of all client objects for Qt.

    """
    _objects = WeakValueDictionary()

    @classmethod
    def lookup_object(cls, object_id):
        return cls._objects.get(object_id)

    @classmethod
    def build(cls, parent, tree, pipe, factories):
        """ Build out a widget tree using the provided info.

        parent : QtObject or None

        tree : dict

        pipe : QActionPipe

        """
        object_id = tree['object_id']
        self = cls(object_id, parent, pipe)
        self.create(tree)
        for child_t in tree['children']:
            for base in child_t['bases']:
                if base in factories:
                    object_cls = factories[base]()
                    obj = object_cls.build(self, child_t, pipe, factories)
                    self.add_child(obj)
                    break
        self.initialize()
        return self
        
    def initialize(self):
        for child in self.children():
            child.initialize()
        self.init_layout()

    def __new__(cls, object_id, *args, **kwargs):
        if object_id in cls._objects:
            raise ValueError('Duplicate object id')
        self = super(QtObject, cls).__new__(cls)
        cls._objects[object_id] = self
        return self

    def __init__(self, object_id, parent=None, pipe=None):
        """ Initialize a QtObject.

        Parameters
        ----------
        object_id : str
            The unique identifier to use with this object.

        parent : QtObject or None
            The parent object of this object, or None if this object
            has no parent.

        pipe : QActionPipe
            The action pipe to use for sending actions to Enaml objects.

        """
        self._object_id = object_id
        self._parent = parent
        self._pipe = pipe
        self._children = []
        self._children_map = {}
        self._widget = None

    #--------------------------------------------------------------------------
    # Messaging/Session API
    #--------------------------------------------------------------------------
    def handle_action(self, action, content):
        """ Handle an action sent from the server widget

        This is called by the QtClientSession object when the server
        widget sends a message to this widget.

        Parameters
        ----------
        action : str
            The action to be performed by the widget.

        content : ObjectDict
            The content dictionary for the action.

        """
        handler_name = 'on_action_' + action
        handler = getattr(self, handler_name, None)
        if handler is not None:
            handler(content)
        else:
            msg = "Unhandled action sent to `%s` from server: %s"
            logging.warn(msg % (self.widget_id(), action))
            
    def send_action(self, action, content):
        """ Send an action to the server widget.

        This method can be called to send an unsolicited message of
        type 'widget_action' to the server widget for this widget.

        Parameters
        ----------
        action : str
            The action for the message.

        content : dict
            The content of the message.

        """
        pipe = self._pipe
        if pipe is not None:
            pipe.send(self._object_id, action, content)

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------
    @property
    def loopback_guard(self):
        """ Lazily creates and returns a LoopbackGuard for convenient 
        use by subclasses.

        """
        try:
            guard = self._loopback_guard
        except AttributeError:
            guard = self._loopback_guard = LoopbackGuard()
        return guard

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def parent(self):
        """ Get the parent of this messenger widget.

        Returns
        -------
        result : QtMessengerWidget or None
            The parent of this messenger widget, or None if it has
            no parent.

        """
        return self._parent

    def children(self):
        """ Get the children of this widget.

        Returns
        -------
        result : list
            The list of children of this widget. This list should not
            be modified in place by user code.

        """
        return self._children

    def add_child(self, child):
        """ Add a child widget to this widget.

        Parameters
        ----------
        child : QtMessengerWidget
            The child widget to add to this widget.

        """
        # XXX handle reparenting and duplicate adding
        self._children.append(child)
        self._children_map[child.widget_id()] = child

    def insert_child(self, index, child):
        """ Insert a child widget into this widget.

        Parameters
        ----------
        index : int
            The target index for the child widget.

        child : QtMessengerWidget
            The child widget to insert into this widget.

        """
        # XXX handle reparenting and duplicates
        self._children.insert(index, child)
        self._children_map[child.widget_id()] = child

    def remove_child(self, child):
        """ Remove the child widget from this widget.

        Parameters
        ----------
        child : QtMessengerWidget
            The child widget to remove from this widget.

        """
        # XXX handle unparenting
        children = self._children
        if child in children:
            children.remove(child)
            self._children_map.pop(child.widget_id(), None)

    def find_child(self, widget_id):
        """ Find the child with the given widget id.

        Parameters
        ----------
        widget_id : str
            The widget identifier for the target widget.

        Returns
        -------
        result : QtMessengerWidget or None
            The child widget or None if its not found.

        """
        return self._children_map.get(widget_id)

    def widget(self):
        """ Get the toolkit widget for this messenger widget.

        Returns
        -------
        result : QWidget
            The toolkit widget for this messenger widget, or None if
            it does not have a toolkit widget.

        """
        return self._widget

    def widget_id(self):
        """ Get the widget id for the messenger widget.

        Returns
        -------
        result : str
            The widget identifier for this messenger widget.

        """
        return self._object_id

    def object_id(self):
        return self._object_id

    def create_widget(self, parent, tree):
        """ A method which must be implemented by subclasses.

        This method is called by the create(...) method. It should 
        create and return the underlying Qt widget. Implementations 
        of this method should *not* call the superclass version.

        Parameters
        ----------
        parent : QWidget or None
            The parent Qt widget for this control, or None if if the
            control does not have a parent.

        tree : dict
            The dictionary representation of the tree for this object.
            This is provided in the even that the component needs to 
            create a different type of widget based on the information
            in the tree.

        """
        raise NotImplementedError

    def create(self, tree):
        """ A method called by the application when creating the UI.

        The default implementation of this method calls 'create_widget'
        and assigns the results to the 'widget' attribute, so subclasses
        must be sure to call the superclass method as the first order of
        business.

        This method is called by the application in a top-down fashion.

        Parameters
        ----------
        tree : dict
            The dictionary representation of the tree for this object.

        """
        parent = self._parent
        parent_widget = parent.widget() if parent else None
        self._widget = self.create_widget(parent_widget, tree)

    def init_layout(self):
        """ A method that allows widgets to do layout initialization.

        This method is called after all widgets in a tree have had
        their 'create' method called. It is useful for doing any
        initialization related to layout.

        The default implementation of this method is a no-op in order
        to be super() friendly.

        This method is called by the application in a bottom-up order.
        
        """
        pass

    def destroy(self):
        """ Destroy this widget.

        Destruction is performed in the following order:
            1. The 'destroy' method is called on all children.
            2. The reference to the children are dropped.
            3. The object removes itself from its parent.
            4. The parent reference is set to None.
            5. The underyling Qt widget is hidden and unparented.
            6. The object removes itself from the session.

        """
        children = self._children
        self._children = []
        self._children_map = {}
        for child in children:
            child.destroy()

        parent = self._parent
        if parent is not None:
            parent.remove_child(self)
        self._parent = None

        widget = self._widget
        if widget is not None:
            widget.hide()
            widget.setParent(None)
        self._widget = None

        session = self._session
        if session is not None:
            session.widget_destroyed(self._widget_id)
            self._session = None

