#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import defaultdict, deque, namedtuple
import logging
import re

from traits.api import (
    HasStrictTraits, Disallow, Property, Str, Enum, ReadOnly, Any,
)

from enaml.utils import make_dispatcher, id_generator

from .trait_types import EnamlEvent


logger = logging.getLogger(__name__)


#: The dispatch function for action dispatching.
dispatch_action = make_dispatcher('on_action_', logger)


#: A namedtuple which contains information about a child change event.
#: The `old` slot will be the ordered list of old children. The `new`
#: slot will be the ordered list of new children.
ChildrenEvent = namedtuple('ChildrenEvent', 'old new')


#: A namedtuple which contains information about a parent change event.
#: The `old` slot will be the old parent and the `new` slot will be
#: the new parent.
ParentEvent = namedtuple('ParentEvent', 'old new')


#: The identifier generator for object instances.
object_id_generator = id_generator('o_')


class ChildrenEventContext(object):
    """ A context manager which will emit a child event on an Object.

    This context manager will automatically emit the child event on an
    Object when the context is exited. This context manager can also be
    safetly nested; only the top-level context for a given object will
    emit the child event, effectively collapsing all transient state.

    """
    #: Class level storage for tracking nested context managers.
    _counters = defaultdict(int)

    def __init__(self, parent):
        """ Initialize a ChildrenEventContext.

        Parameters
        ----------
        parent : Object or None
            The Object on which to emit a child event on context exit.
            To make it easier for reparenting operations, the parent
            can be None.

        """
        self._parent = parent

    def __enter__(self):
        """ Enter the children event context.

        This method will snap the current child state of the parent and
        use it to diff the state on context exit.

        """
        parent = self._parent
        counters = self._counters
        count = counters[parent]
        counters[parent] = count + 1
        if count == 0 and parent is not None:
            self._old = parent._children

    def __exit__(self, exc_type, exc_value, traceback):
        """ Exit the children event context.

        If this context manager is the top-level manager for the parent
        object *and* no exception occured in the context, then a child
        event will be emitted on the parent. Any exception raised during
        the context is propagated.

        """
        parent = self._parent
        counters = self._counters
        counters[parent] -= 1
        if counters[parent] == 0:
            del counters[parent]
            if exc_type is None and parent is not None:
                old = self._old
                new = parent._children
                if old != new:
                    evt = ChildrenEvent(old, new)
                    parent.children_event(evt)


class Object(HasStrictTraits):
    """ The most base class of the Enaml object hierarchy.

    An Enaml Object provides supports parent-children relationships and
    provides facilities for initializing, navigating, searching, and
    destroying the tree. It also contains methods for sending messages
    between objects when the object is part of a session.

    """
    #: An optional name to give to this object to assist in finding it
    #: in the tree (see . the 'find' method. Note that there is no
    #: guarantee of uniqueness for an object `name`. It is left to the
    #: developer to choose an appropriate name.
    name = Str

    #: A read-only property which returns the object's parent. This
    #: will be an instance Object or None if there is no parent. A
    #: strong reference is kept to the parent object.
    parent = Property(fget=lambda self: self._parent)

    #: A read-only property which returns the objects children. This
    #: will be an iterable of Object instances. A strong reference is
    #: kept to all child objects.
    children = Property(fget=lambda self: self._children)

    #: An event fired when an the oject has been initialized. It is
    #: emitted once during an object's lifetime, when the object is
    #: initialized by a Session.
    initialized = EnamlEvent

    #: An event fired when an object has been activated. It is emitted
    #: once during an object's lifetime, when the object is activated
    #: by a Session.
    activated = EnamlEvent

    #: An event fired when an object is being destroyed. This event
    #: is fired once during the object lifetime, just before the
    #: object is removed from the tree structure.
    destroyed = EnamlEvent

    #: A read-only property which returns the object's session. This
    #: will be an instance of Session or None if there is no session.
    #: A strong reference is kept to the session object. This value
    #: should not be manipulated by user code.
    session = Property(fget=lambda self: self._session)

    #: A read-only value which returns the object's identifier. This
    #: will be computed the first time it is requested. The default
    #: value is guaranteed to be unique for the current process. The
    #: initial value may be supplied by user code if more control is
    #: required, with proper care that the value is a unique string.
    object_id = ReadOnly
    def _object_id_default(self):
        return object_id_generator.next()

    #: The current state of the object in terms of its lifetime within
    #: a session. This value should not be manipulated by user code.
    state = Enum(
        'inactive', 'initializing', 'initialized', 'activating', 'active',
        'destroying', 'destroyed',
    )

    #: A read-only property which is True if the object is inactive.
    is_inactive = Property(fget=lambda self: self.state == 'inactive')

    #: A read-only property which is True if the object is initializing.
    is_initializing = Property(fget=lambda self: self.state == 'initializing')

    #: A read-only property which is True if the object is initialized.
    is_initialized = Property(fget=lambda self: self.state == 'initialized')

    #: A read-only property which is True if the object is activating.
    is_activating = Property(fget=lambda self: self.state == 'activating')

    #: A read-only property which is True if the object is active.
    is_active = Property(fget=lambda self: self.state == 'active')

    #: A read-only property which is True if the object is destroying.
    is_destroying = Property(fget=lambda self: self.state == 'destroying')

    #: A read-only property which is True if the object is destroyed.
    is_destroyed = Property(fget=lambda self: self.state == 'destroyed')

    #: Private storage traits. These should *never* be manipulated by
    #: user code. For performance reasons, these are not type-checked.
    _parent = Any       # Object or None
    _children = Any     # tuple of Object
    _session = Any      # Session or None

    def __init__(self, parent=None, **kwargs):
        """ Initialize an Object.

        Parameters
        ----------
        parent : Object or None, optional
            The Object instance which is the parent of this object, or
            None if the object has no parent. Defaults to None.

        **kwargs
            Additional keyword arguments to apply to the object after
            the parent has been set.

        """
        super(Object, self).__init__()
        self._parent = None
        self._children = ()
        if parent is not None:
            self.set_parent(parent)
        if kwargs:
            # `trait_set` is slow, don't use it here.
            for key, value in kwargs.iteritems():
                setattr(self, key, value)

    #--------------------------------------------------------------------------
    # Lifetime API
    #--------------------------------------------------------------------------
    def initialize(self):
        """ Called by a Session to initialize the object tree.

        This method is called by a Session object to allow the object
        tree to perform initialization before the object is activated
        for messaging.

        """
        self.state = 'initializing'
        self.pre_initialize()
        for child in self.children:
            child.initialize()
        self.state = 'initialized'
        self.post_initialize()

    def pre_initialize(self):
        """ Called during the initialization pass before any children
        are initialized.

        The object `state` during this call will be 'initializing'.

        """
        pass

    def post_initialize(self):
        """ Called during the initialization pass after all children
        have been initialized.

        The object `state` during this call will be 'initialized'. The
        default implementation of this method emits the `initialized`
        event.

        """
        self.initialized()

    def activate(self, session):
        """ Called by a Session to activate the object tree.

        This method is called by a Session object to activate the object
        tree for messaging.

        Parameters
        ----------
        session : Session
            The session to use for messaging with this object tree.

        """
        self.state = 'activating'
        self.pre_activate(session)
        self._session = session
        session.register(self)
        for child in self._children:
            child.activate(session)
        self.state = 'active'
        self.post_activate(session)

    def pre_activate(self, session):
        """ Called during the activation pass before any children are
        activated.

        The object `state` during this call will be 'activating'.

        Parameters
        ----------
        session : Session
            The session to use for messaging with this object tree.

        """
        pass

    def post_activate(self, session):
        """ Called during the activation pass after all children are
        activated.

        The object `state` during this call will be 'active'. The
        default implementation emits the `activated` event.

        Parameters
        ----------
        session : Session
            The session to use for messaging with this object tree.

        """
        self.activated()

    def destroy(self):
        """ Destroy this object and all of its children recursively.

        This will emit the `destroyed` event before any change to the
        object tree is made. After this returns, the object should be
        considered invalid and should no longer be used.

        """
        # Only send the destroy message if the object's parent is not
        # being destroyed. This reduces the number of messages since
        # the automatic destruction of children is assumed.
        parent = self._parent
        if parent is None or not parent.is_destroying:
            self.batch_action('destroy', {})
        self.state = 'destroying'
        self.pre_destroy()
        if self._children:
            for child in self._children:
                child.destroy()
            self._children = ()
        if parent is not None:
            if parent.is_destroying:
                self._parent = None
            else:
                self.set_parent(None)
        session = self._session
        if session is not None:
            session.unregister(self)
        self.state = 'destroyed'
        self.post_destroy()

    def pre_destroy(self):
        """ Called during the destruction pass before any children are
        destroyed.

        The object `state` during this call will be 'destroying'. The
        default implementation emits the `destroyed` event.

        """
        self.destroyed()

    def post_destroy(self):
        """ Called during the destruction pass after all children are
        destroyed.

        The object `state` during this call will be 'destroyed'. This
        allows subclasses to perform cleanup once the object has been
        fully removed from the hierarchy.

        """
        pass

    #--------------------------------------------------------------------------
    # Parenting API
    #--------------------------------------------------------------------------
    def set_parent(self, parent):
        """ Set the parent for this object.

        If the parent is not None, the child will be appended to the end
        of the parent's children. If the parent is already the parent of
        this object, then this method is a no-op. If this object already
        has a parent, then it will be properly reparented.

        Parameters
        ----------
        parent : Object or None
            The Object instance to use for the parent, or None if this
            object should be unparented.

        Notes
        -----
        It is the responsibility of the caller to initialize and activate
        the object as needed, if it is reparented dynamically at runtime.

        """
        old_parent = self._parent
        if parent is old_parent:
            return
        if parent is self:
            raise ValueError('cannot use `self` as Object parent')
        if parent is not None and not isinstance(parent, Object):
            raise TypeError('parent must be an Object or None')
        self._parent = parent
        self.parent_event(ParentEvent(old_parent, parent))
        if old_parent is not None:
            old_kids = old_parent._children
            idx = old_kids.index(self)
            with old_parent.children_event_context():
                old_parent._children = old_kids[:idx] + old_kids[idx + 1:]
        if parent is not None:
            with parent.children_event_context():
                parent._children += (self,)

    def insert_children(self, before, insert):
        """ Insert children into this object at the given location.

        The children will be automatically parented and inserted into
        the object's children. If any children are already children of
        this object, then they will be moved appropriately.

        Parameters
        ----------
        before : Object or None
            A child object to use as the marker for inserting the new
            children. The new children will be inserted directly before
            this marker. If the Object is None or not a child, then the
            new children will be added to the end of the children.

        insert : iterable
            An iterable of Object children to insert into this object.

        Notes
        -----
        It is the responsibility of the caller to initialize and activate
        the object as needed, if it is reparented dynamically at runtime.

        """
        insert_tup = tuple(insert)
        insert_set = set(insert_tup)
        if self in insert_set:
            raise ValueError('cannot use `self` as Object child')
        if len(insert_tup) != len(insert_set):
            raise ValueError('cannot insert duplicate children')
        if not all(isinstance(child, Object) for child in insert_tup):
            raise TypeError('children must be an Object instances')

        new = []
        added = False
        for child in self._children:
            if child in insert_set:
                continue
            if child is before:
                new.extend(insert_tup)
                added = True
            new.append(child)
        if not added:
            new.extend(insert_tup)

        for child in insert_tup:
            old_parent = child._parent
            if old_parent is not self:
                child._parent = self
                child.parent_event(ParentEvent(old_parent, self))
                if old_parent is not None:
                    old_kids = old_parent._children
                    idx = old_kids.index(child)
                    old_kids = old_kids[:idx] + old_kids[idx + 1:]
                    with old_parent.children_event_context():
                        old_parent._children = old_kids

        with self.children_event_context():
            self._children = tuple(new)

    def parent_event(self, event):
        """ Handle a `ParentEvent` posted to this object.

        This event handler is called when the parent on the object has
        changed, but before the children of the new parent have been
        updated. There is no guarantee that the parent has been fully
        initialized when this is called. Sublasses may reimplement this
        method as required. The default implementation emits the trait
        change notification, so subclasses which override the default
        must be sure to call the superclass version, or emit the trait
        change themselves.

        Parameters
        ----------
        event : ParentEvent
            The event for the parent change of this object.

        """
        self.trait_property_changed('parent', event.old, event.new)

    def children_event(self, event):
        """ Handle a `ChildrenEvent` posted to this object.

        This event handler is called by a `ChildrenEventContext` when
        the last nested context is exited. There is no guarantee that
        the children will be fully initialized when this is called.
        Sublasses may reimplement this method as required. The default
        implementation emits the trait change notification, so
        subclasses which override the default must be sure to call the
        superclass version, or emit the trait change themselves.

        Parameters
        ----------
        event : ChildrenEvent
            The event for the children change of this object.

        """
        self.trait_property_changed('children', event.old, event.new)

    def children_event_context(self):
        """ Get a context manager for sending children events.

        This method should be called and entered whenever the children
        of an object are changed. The returned context manager will
        collapse all nested changes into a single aggregate event.

        Returns
        -------
        result : ChildrenEventContext
            The context manager which should be entered before changing
            the children of the object.

        """
        return ChildrenEventContext(self)

    #--------------------------------------------------------------------------
    # Messaging API
    #--------------------------------------------------------------------------
    def send_action(self, action, content):
        """ Send an action to the client of this object.

        The action will only be sent if the current state of the object
        is `active`. Subclasses may reimplement this method if more
        control is needed.

        Parameters
        ----------
        action : str
            The name of the action which the client should perform.

        content : dict
            The content data for the action.

        """
        if self.is_active:
            self._session.send(self.object_id, action, content)

    def batch_action(self, action, content):
        """ Batch an action to be sent to the client at a later time.

        The action will only be batched if the current state of the
        object is `active`. Subclasses may reimplement this method
        if more control is needed.

        Parameters
        ----------
        action : str
            The name of the action which the client should perform.

        content : dict
            The content data for the action.

        """
        if self.is_active:
            self._session.batch(self.object_id, action, content)

    def batch_action_task(self, action, task):
        """ Similar to `batch_action` but takes a callable task.

        The task will only be batched if the current state of the
        object is `active`. Subclasses may reimplement this method
        if more control is needed.

        Parameters
        ----------
        action : str
            The name of the action which the client should perform.

        task : callable
            A callable which will be invoked at a later time. It must
            return the content dictionary for the action.

        """
        if self.is_active:
            self._session.batch_task(self.object_id, action, task)

    def receive_action(self, action, content):
        """ Receive an action from the client of this object.

        The default implementation will dynamically dispatch the action
        to specially named handlers if the current state of the object
        is 'active'. Subclasses may reimplement this method if more
        control is needed.

        Parameters
        ----------
        action : str
            The name of the action to perform.

        content : dict
            The content data for the action.

        """
        if self.is_active:
            dispatch_action(self, action, content)

    #--------------------------------------------------------------------------
    # Object Tree API
    #--------------------------------------------------------------------------
    def root_object(self):
        """ Get the root object for this hierarchy.

        Returns
        -------
        result : Object
            The top-most object in the hierarchy to which this object
            belongs.

        """
        obj = self
        while obj._parent is not None:
            obj = obj._parent
        return obj

    def traverse(self, depth_first=False):
        """ Yield all of the objects in the tree, from this object down.

        Parameters
        ----------
        depth_first : bool, optional
            If True, yield the nodes in depth first order. If False,
            yield the nodes in breadth first order. Defaults to False.

        """
        if depth_first:
            stack = [self]
            stack_pop = stack.pop
            stack_extend = stack.extend
        else:
            stack = deque([self])
            stack_pop = stack.popleft
            stack_extend = stack.extend
        while stack:
            obj = stack_pop()
            yield obj
            stack_extend(obj._children)

    def traverse_ancestors(self, root=None):
        """ Yield all of the objects in the tree, from this object up.

        Parameters
        ----------
        root : Object, optional
            The object at which to stop traversal. Defaults to None.

        """
        parent = self._parent
        while parent is not root and parent is not None:
            yield parent
            parent = parent._parent

    def find(self, name, regex=False):
        """ Find the first object in the subtree with the given name.

        This method will traverse the tree of objects, breadth first,
        from this object downward, looking for an object with the given
        name. The first object with the given name is returned, or None
        if no object is found with the given name.

        Parameters
        ----------
        name : string
            The name of the object for which to search.

        regex : bool, optional
            Whether the given name is a regex string which should be
            matched against the names of children instead of tested
            for equality. Defaults to False.

        Returns
        -------
        result : Object or None
            The first object found with the given name, or None if no
            object is found with the given name.

        """
        if regex:
            rgx = re.compile(name)
            match = lambda n: bool(rgx.match(n))
        else:
            match = lambda n: n == name
        for obj in self.traverse():
            if match(obj.name):
                return obj

    def find_all(self, name, regex=False):
        """ Find all objects in the subtree with the given name.

        This method will traverse the tree of objects, breadth first,
        from this object downward, looking for a objects with the given
        name. All of the objects with the given name are returned as a
        list.

        Parameters
        ----------
        name : string
            The name of the objects for which to search.

        regex : bool, optional
            Whether the given name is a regex string which should be
            matched against the names of objects instead of testing
            for equality. Defaults to False.

        Returns
        -------
        result : list of Object
            The list of objects found with the given name, or an empty
            list if no objects are found with the given name.

        """
        if regex:
            rgx = re.compile(name)
            match = lambda n: bool(rgx.match(n))
        else:
            match = lambda n: n == name
        res = []
        push = res.append
        for obj in self.traverse():
            if match(obj.name):
                push(obj)
        return res

    #--------------------------------------------------------------------------
    # HasTraits Fixes
    #--------------------------------------------------------------------------
    #: The HasTraits class defines a class attribute 'set' which is a
    #: deprecated alias for the 'trait_set' method. The problem is that
    #: having that as an attribute interferes with the ability of Enaml
    #: expressions to resolve the builtin 'set', since dynamic scoping
    #: takes precedence over builtins. This resets those ill-effects.
    set = Disallow

    def add_notifier(self, name, notifier):
        """ Add a notifier to a trait on the object.

        This is different from `on_trait_change` in that it allows the
        developer to provide the notifier object directly. This allows
        the possibility of more efficient notifier patterns.

        """
        self._trait(name, 2)._notifiers(1).append(notifier)

