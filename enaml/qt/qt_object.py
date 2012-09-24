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
    #: Class level storage for QtObject instances. QtObjects are added 
    #: to this dict as they are created. Instances are stored weakly.
    _objects = WeakValueDictionary()

    @classmethod
    def lookup_object(cls, object_id):
        """ A classmethod which finds the object with the given id.

        Parameters
        ----------
        object_id : str
            The identifier for the object to lookup.

        Returns
        -------
        result : QtObject or None
            The QtObject for the given identifier, or None if no object
            is found.

        """
        return cls._objects.get(object_id)

    @classmethod
    def construct(cls, tree, parent, pipe):
        """ Construct the QtObject instance for the given parameters.

        This classmethod is called by the QtBuilder object used by the
        application. When called, it will create a new instance of the 
        class by extracting the object id from the snapshot and calling 
        the class constructor. It then invokes the `create` method on
        the new instance. This classmethod exists for cases where it is
        necessary to define custom construction behavior. A subclass 
        may reimplement this method as required.

        Parameters
        ----------
        tree : dict
            An Enaml snapshot dict representing an object tree from this
            object downward.

        parent : QtObject or None
            The parent QtObject to use for this object, or None if this
            object is top-level.

        pipe : QActionPipe
            The QActionPipe to use for sending messages to the Enaml
            widget.

        Returns
        -------
        result : QtObject
            The QtObject instance for these parameters.

        Notes
        -----
        This method does *not* construct the children for this object.
        That responsibility lies with the QtBuilder object which calls
        this constructor.

        """
        object_id = tree['object_id']
        self = cls(object_id, parent, pipe)
        self.create(tree)
        return self

    def __new__(cls, object_id, *args, **kwargs):
        """ Create a new QtObject.

        If the provided object id already exists, an exception will be
        raised.

        Parameters
        ----------
        object_id : str
            The unique object identifier assigned to this object.

        *args, **kwargs
            Additional positional and keyword arguments needed to 
            initialize a QtObject.

        Returns
        -------
        result : QtObject
            A new QtObject instance.

        """
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
        self._initialized = False

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
    # Object Methods
    #--------------------------------------------------------------------------
    def object_id(self):
        """ Get the object id for the object.

        Returns
        -------
        result : str
            The unique identifier for this object.

        """
        return self._object_id

    def widget_id(self):
        """ A backwards compatibility method. New code should call the
        `object_id` method.

        """
        return self._object_id

    def widget(self):
        """ Get the toolkit-specific object for this object.

        Returns
        -------
        result : QObject
            The toolkit object for this object, or None if it does not 
            have a toolkit object.

        """
        return self._widget

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

    def initialized(self):
        """ Get whether or not this object is initialized.

        Returns
        -------
        result : bool
            True if this object has been initialized, False otherwise.

        """
        return self._initialized

    def initialize(self):
        """ A method called by the application to initialize the UI.

        This method is called by the application to allow the object
        tree perform any post-create initialization required. This 
        method should only be called once. Multiple calls to this
        method are ignored.

        """
        if not self._initialized:
            for child in self.children():
                child.initialize()
            self.init_layout()
            self._initialized = True

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
        # XXX revisit this!!
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

    #--------------------------------------------------------------------------
    # Parenting Methods
    #--------------------------------------------------------------------------
    def parent(self):
        """ Get the parent of this QtObject.

        Returns
        -------
        result : QtObject or None
            The parent object of this object, or None if it has no 
            parent.

        """
        return self._parent

    def children(self):
        """ Get the children of this object.

        Returns
        -------
        result : list
            The list of children of this object. This list should not
            be modified in place by user code.

        """
        return self._children

    def add_child(self, child):
        """ Add a child widget to this object.

        Parameters
        ----------
        child : QtObject
            The child object to add to this object.

        """
        # XXX handle reparenting and duplicate adding
        self._children.append(child)
        self._children_map[child.object_id()] = child

    def insert_child(self, index, child):
        """ Insert a child object into this object.

        Parameters
        ----------
        index : int
            The target index for the child object.

        child : QtObject
            The child object to insert into this object.

        """
        # XXX handle reparenting and duplicates
        self._children.insert(index, child)
        self._children_map[child.object_id()] = child

    def remove_child(self, child):
        """ Remove the child object from this object.

        Parameters
        ----------
        child : QtObject
            The child object to remove from this object.

        """
        # XXX handle unparenting
        children = self._children
        if child in children:
            children.remove(child)
            self._children_map.pop(child.object_id(), None)

    def find_child(self, object_id):
        """ Find the child with the given object id.

        Parameters
        ----------
        object_id : str
            The object identifier for the target object.

        Returns
        -------
        result : QtObject or None
            The child object or None if it is not found.

        """
        return self._children_map.get(object_id)

    #--------------------------------------------------------------------------
    # Messaging Methods
    #--------------------------------------------------------------------------
    def handle_action(self, action, content):
        """ Handle an action sent from an Enaml widget.

        This method tells the object to handle a specific action. The 
        default behavior of the method is to dispatch the action to a 
        handler method named `on_action_<action>` where <action> is
        substituted with the provided action.

        Parameters
        ----------
        action : str
            The action to be performed by the object.

        content : dict
            The content dictionary for the action.

        """
        handler_name = 'on_action_' + action
        handler = getattr(self, handler_name, None)
        if handler is not None:
            handler(content)
        else:
            msg = "Unhandled action '%s' for QtObject %s:%s"
            logging.warn(msg % (action, type(self).__name__, self._object_id))
            
    def send_action(self, action, content):
        """ Send an action on the action pipe for this object.

        Parameters
        ----------
        action : str
            The name of the action performed.

        content : dict
            The content data for the action.

        """
        pipe = self._pipe
        if pipe is not None:
            pipe.send(self._object_id, action, content)

