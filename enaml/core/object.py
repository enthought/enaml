#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import defaultdict, deque, namedtuple
import logging
import re

from traits.api import Property, Str, Enum, ReadOnly

from enaml.utils import make_dispatcher, id_generator

from .has_traits_patch import HasPrivateTraits_Patched
from .trait_types import EnamlEvent


#: The logger for the `object` module.
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
obj_id_generator = id_generator('o_')


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
        parent : Object
            The Object on which to emit a child event on context exit.

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
        if count == 0:
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
            if exc_type is None:
                old = self._old
                new = parent._children
                if old != new:
                    evt = ChildrenEvent(old, new)
                    parent.children_event(evt)


class Object(HasPrivateTraits_Patched):
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
    #: emitted once during an object's lifetime, before the object
    #: has been registered with a session.
    initialized = EnamlEvent

    #: An event fired when an object has been activated. It is emitted
    #: once during an object's lifetime, once it has been registered
    #: with a session.
    activated = EnamlEvent

    #: An event fired when an object is being destroyed. This event
    #: is fired once during the object lifetime, before any change to
    #: the tree structure is made and allows any listeners to perform
    #: last minute cleanup.
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
    #: needed, with sufficient care that the value is unique.
    object_id = ReadOnly
    def _object_id_default(self):
        return obj_id_generator.next()

    #: The current state of the object for purposes of messaging. This
    #: value should not be manipulated directly by user code.
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

    def initialize(self):
        """ Called by a session to initialize the object tree.

        This method is called by a Session object to allow the object
        tree to perform additional initialization before it is activated
        for messaging. Subclasses which modify the object tree during
        the initialization pass are responsible for ensuring that new
        children are initialized.

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
        tree for messaging. Subclasses must not modify the object tree
        during activation.

        Parameters
        ----------
        session : Session
            The session object to use for messaging with this object
            tree.

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
            The session object to use for messaging with this object
            tree.

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
            The session object to use for messaging with this object
            tree.

        """
        self.activated()

    def destroy(self):
        """ Destroy this object and all of its children recursively.

        This will emit the `destroyed` event before any change to the
        object tree is made. This method will set the `state` flag to
        'destroying'. After this method returns, the object should be
        considered invalid and no longer be used.

        """
        self.pre_destroy()
        self.state = 'destroying'
        if self._children:
            for child in self._children:
                child.destroy()
            self._children = ()
        parent = self._parent
        if parent is not None and parent.is_destroying:
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

        The object `state` during this call will be 'active'.
        default implementation emits the `destroyed` event.

        """
        self.destroyed()

    def post_destroy(self):
        """ Called during the destruction pass after all children are
        destroyed.

        This allows subclass to perform any required cleanup after
        everything on the base object has been closed.

        """
        pass

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
        It is the responsibility of the caller to intialize and activate
        the object if it is parented dynamically at runtime.

        """
        old_parent = self._parent
        if parent is old_parent:
            return
        if parent is self:
            raise ValueError('cannot use `self` as Object parent')
        if parent is not None and not isinstance(parent, Object):
            raise TypeError('parent must be an Object or None')
        self._parent = parent
        evt = ParentEvent(old_parent, parent)
        self.parent_event(evt)
        if old_parent is not None:
            old_kids = old_parent._children
            idx = old_kids.index(self)
            with ChildrenEventContext(old_parent):
                old_parent._children = old_kids[:idx] + old_kids[idx + 1:]
        if parent is not None:
            with ChildrenEventContext(parent):
                parent._children += (self,)

    def permute_children(self, permuation):
        """ Permute the ordering of the object's children.

        This method will emit a `ChildrenEvent` upon completion.

        Parameters
        ----------
        permutation : iterable of int
            An iterable of integers specifing the permutation to apply
            to the children.

        """
        with ChildrenEventContext(self):
            curr = self._children
            self._children = tuple(curr[idx] for idx in permuation)

    def parent_event(self, event):
        """ Handle a `ParentEvent` posted to this object.

        This event handler is called when the parent on the object has
        changed, but before the children of the new parent have been
        updated. Sublasses may reimplement this method as required, but
        should nearly always call super() so that the trait notification
        is emitted.

        Parameters
        ----------
        event : ParentEvent
            The event for the parent change of this object.

        """
        self.trait_property_changed('parent', event.old, event.new)

    def children_event(self, event):
        """ Handle a `ChildrenEvent` posted to this object.

        This event handler is called by a `ChildrenEventContext` when
        the last nested context is exited. Sublasses may reimplement
        this method as required, but should nearly always call super()
        so that the trait notification is emitted.

        Parameters
        ----------
        event : ChildrenEvent
            The event for the children change of this object.

        """
        self.trait_property_changed('children', event.old, event.new)

    def send_action(self, action, content):
        """ Send an action to the client of this object.

        The action will only be sent if the object state is `active`.
        Subclasses may reimplement this method if more control is needed.

        Parameters
        ----------
        action : str
            The name of the action performed.

        content : dict
            The content data for the action.

        """
        if self.is_active:
            self._session.send(self.object_id, action, content)

    def receive_action(self, action, content):
        """ Receive an action from the client of this messenger.

        The default implementation will dynamically dispatch the message
        to specially named handlers if the object `state` is 'active'.
        Subclasses may reimplement this method if more control is needed.

        Parameters
        ----------
        action : str
            The name of the action to perform.

        content : dict
            The content data for the action.

        """
        if self.is_active:
            dispatch_action(self, action, content)

    def traverse(self, depth_first=False):
        """ Yields all of the object in the tree, from this object down.

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
            item = stack_pop()
            yield item
            stack_extend(item._children)

    def traverse_ancestors(self, root=None):
        """ Yields all of the objects in the tree, from the parent of
        this object up, stopping at the given root.

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
        """ Return the first named object that exists in the subtree.

        This method will traverse the tree of objects, breadth first,
        from this object downward, looking for an object with the given
        name. The first one with the given name is returned, or None if
        no object is found.

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
            The first object found with the given name, or None if
            no object is found.

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
        """ Return all the named objects that exist in the subtree.

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
            list if no objects are found.

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

