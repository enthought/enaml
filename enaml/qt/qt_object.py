#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import functools
import logging

from enaml.utils import LoopbackGuard

from .qt.QtCore import QObject
from .q_deferred_caller import QDeferredCaller


def deferred_updates(func):
    """ A method decorator which will defer widget updates.

    When used as a decorator for a QtObject, this will disable updates
    on the underlying widget, and re-enable them on the next cycle of
    the event loop after the method returns.

    Parameters
    ----------
    func : function
        A function object defined as a method on a QtObject.

    """
    @functools.wraps(func)
    def closure(self, *args, **kwargs):
        widget = self.widget()
        if widget is not None and widget.isWidgetType():
            widget.setUpdatesEnabled(False)
            try:
                res = func(self, *args, **kwargs)
            finally:
                QtObject.deferred_call(widget.setUpdatesEnabled, True)
        else:
            res = func(self, *args, **kwargs)
        return res
    return closure


class QtObject(object):
    """ The most base class of all client objects for the Enaml Qt 
    implementation.

    """
    #: Class level storage for QtObject instances. QtObjects are added 
    #: to this dict as they are created. Instances are stored strongly
    #: so that orphaned widgets are not garbage collected until they 
    #: are explicitly destroyed.
    _objects = {}

    #: A class level deferred caller. Created on demand.
    _deferred_caller = None

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
    def construct(cls, tree, parent, pipe, builder):
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

        pipe : QActionPipe or None
            The QActionPipe to use for sending messages to the Enaml
            object, or None if messaging is not desired.

        builder : QtBuilder
            The QtBuilder instance that is building this object.

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
        self = cls(object_id, parent, pipe, builder)
        self.create(tree)
        return self

    @classmethod
    def deferred_call(cls, callback, *args, **kwargs):
        """ Execute the callback on the main gui thread.

        Parameters
        ----------
        callback : callable
            The callable object to execute on the main thread.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        caller = cls._deferred_caller
        if caller is None:
            caller = cls._deferred_caller = QDeferredCaller()
        caller.deferredCall(callback, *args, **kwargs)

    @classmethod
    def timed_call(cls, ms, callback, *args, **kwargs):
        """ Execute a callback on timer in the main gui thread.

        Parameters
        ----------
        ms : int
            The time to delay, in milliseconds, before executing the
            callable.

        callback : callable
            The callable object to execute at on the timer.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        caller = cls._deferred_caller
        if caller is None:
            caller = cls._deferred_caller = QDeferredCaller()
        caller.timedCall(ms, callback, *args, **kwargs)

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

    def __init__(self, object_id, parent, pipe, builder):
        """ Initialize a QtObject.

        Parameters
        ----------
        object_id : str
            The unique identifier to use with this object.

        parent : QtObject or None
            The parent object of this object, or None if this object
            has no parent.

        pipe : QActionPipe or None
            The action pipe to use for sending actions to Enaml objects.

        builder : QtBuilder
            The QtBuilder instance that built this object.

        """
        self._object_id = object_id
        self._pipe = pipe
        self._builder = builder
        self._parent = None
        self._children = []
        self._widget = None
        self._initialized = False
        self.set_parent(parent)

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
        """ A method which should be reimplemented by subclasses.

        This method is called by the create(...) method. It should 
        create and return the underlying Qt widget. Implementations 
        of this method should *not* call the superclass version.

        Parameters
        ----------
        parent : QObject or None
            The parent Qt toolkit object for this control, or None if
            the control does not have a parent.

        tree : dict
            The dictionary representation of the tree for this object.
            This is provided in the even that the component needs to 
            create a different type of widget based on the information
            in the tree.

        """
        return QObject()

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
        """ Destroy this object.

        After an object is destroyed, it is no longer usable and should
        be discarded. All internal references to the object will be 
        removed.

        """
        self._initialized = False

        children = self._children
        self._children = []
        for child in children:
            child.destroy()

        self.set_parent(None)

        widget = self._widget
        if widget is not None:
            # XXX not sure if we should be doing this. It would be better
            # have each relevant widget override the destroy() method and
            # disconnect their handlers.
            widget.blockSignals(True)
            widget.setParent(None)
            self._widget = None

        QtObject._objects.pop(self._object_id, None)

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

    @deferred_updates
    def set_parent(self, parent):
        """ Set the parent for this object.

        If the parent is already initialized, then the `child_removed`
        and `child_added` events will be emitted on the parent. Updates
        on the widget are disabled until after the child events on the
        parent have been processed.

        Parameters
        ----------
        parent : QtObject or None
            The parent of this object, or None if it has no parent.

        """
        # Note: The added/removed events must be executed on the next
        # cycle of the event loop. It's possible that this method is
        # being called from the `construct` class method and the child
        # of the widget will not yet exist. This means that child event
        # handlers that rely on the child widget existing will fail.
        curr = self._parent
        if curr is parent or parent is self:
            return

        self._parent = parent
        if curr is not None:
            if self in curr._children:
                curr._children.remove(self)
                if curr._initialized:
                    QtObject.deferred_call(curr.child_removed, self)

        if parent is not None:
            parent._children.append(self)
            if parent._initialized:
                QtObject.deferred_call(parent.child_added, self)

    def child_removed(self, child):
        """ Called when a child is removed from this object.

        The default implementation of this method unparents the toolkit
        widget if the parent of the child is None. Subclasses which need 
        more control may reimplement this method.

        Parameters
        ----------
        child : QtObject
            The child object removed from this object.

        """
        if child._parent is None:
            widget = child._widget
            if widget is not None:
                widget.setParent(None)

    def child_added(self, child):
        """ A method called when a child is added to this object.

        The default implementation ensures that the toolkit widget is 
        properly parented. Subclasses which need more control may 
        reimplement this method.

        Parameters
        ----------
        child : QtObject
            The child object added to this object.

        """
        widget = child._widget
        if widget is not None:
            widget.setParent(self._widget)

    def index_of(self, child):
        """ Return the index of the given child.

        Parameters
        ----------
        child : QtObject
            The child of interest.

        Returns
        -------
        result : int
            The index of the given child, or -1 if it is not found.

        """
        children = self._children
        if child in children:
            return children.index(child)
        return -1

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

    #--------------------------------------------------------------------------
    # Action Handlers
    #--------------------------------------------------------------------------
    @deferred_updates
    def on_action_children_changed(self, content):
        """ Handle the 'children_changed' action from the Enaml object.

        This method will unparent the removed children and add the new
        children to this object. If a given new child does not exist, it
        will be built. Subclasses that need more control may reimplement
        this method. The default implementation disables updates on the
        widget while adding children and reenables them on the next cyle
        of the event loop.

        """
        # Unparent the children being removed. Destroying a widget is
        # handled through a separate message.
        lookup = QtObject.lookup_object
        for object_id in content['removed']:
            child = lookup(object_id)
            if child is not None and child._parent is self:
                child.set_parent(None)

        # Build or reparent the children being added.
        pipe = self._pipe
        builder = self._builder
        for tree in content['added']:
            object_id = tree['object_id']
            child = lookup(object_id)
            if child is not None:
                child.set_parent(self)
            else:
                child = builder.build(tree, self, pipe)
                child.initialize()

        # Update the ordering of the children based on the order given
        # in the message. If the given order does not include all of
        # the current children, then the ones not included will be
        # appended to the end of the new list in an undefined order.
        ordered = []
        curr_set = set(self._children)
        for object_id in content['order']:
            child = lookup(object_id)
            if child is not None and child._parent is self:
                ordered.append(child)
                curr_set.discard(child)
        ordered.extend(curr_set)
        self._children = ordered

    def on_action_destroy(self, content):
        """ Handle the 'destroy' action from the Enaml object.

        This method will call the `destroy` method on the object.

        """
        self.destroy()

