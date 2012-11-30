#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import defaultdict, deque, namedtuple
import logging
import re

from traits.api import Property, Str

from enaml.utils import make_dispatcher

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


#: A lazily imported class to avoid a circular import.
SessionClass = None


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

    #: An event fired when an object is being destroyed. This event
    #: is fired before an change to the tree structure is made and
    #: allows any listeners to perform last-minute cleanup.
    destroyed = EnamlEvent

    #: A read-only property which returns the object's session. This
    #: will be an instance of Session or None if there is no session.
    #: A strong reference is kept to the session object.
    session = Property(fget=lambda self: self._session)

    #: A unique identifier which will be supplied by a Session when
    #: the object becomes a member of the session. This identifier
    #: should not be edited directly by user code.
    object_id = Str

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

    def destroy(self):
        """ Destroy this object and all of its children recursively.

        This will emit the `destroyed` event before any change to the
        object tree is made. After this method returns, the object is
        considered invalid and should no longer be used.

        """
        self.destroyed()
        if self._children:
            for child in self._children:
                child._destroying = True
                child.destroy()
            self._children = ()
        if self._destroying:
            self._parent = None
        else:
            self.set_parent(None)
        session = self._session
        if session is not None:
            session.unregister(self)
            self._session = None

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
            session = self._session
            psession = parent._session
            if session is not psession:
                self.set_session(psession)
            with ChildrenEventContext(parent):
                parent._children += (self,)

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

    def set_session(self, session):
        """ Set the session for the object.

        This will update the value of the session on this object and on
        every object in the subtree. Each object in the subtree will be
        registered with the session. An error will be raised if the
        object has a parent with a different session.

        Parameters
        ----------
        session : Session
            The session with which the object and its subtree should be
            registered.

        """
        # lazily import the Session class to avoid a circular condition
        global SessionClass
        if SessionClass is None:
            from enaml.session import Session
            SessionClass = Session
        if session is not None and not isinstance(session, SessionClass):
            raise TypeError('session must be a Session or None')
        parent = self._parent
        if parent is not None:
            psession = parent._session
            if psession is not None and psession is not session:
                msg = 'a child cannot have a session different from its parent'
                raise ValueError(msg)
        if session is None:
            for node in self.traverse():
                nsession = node._session
                if nsession is not None:
                    nsession.unregister(node)
                    node._session = None
        else:
            register = session.register
            for node in self.traverse():
                nsession = node._session
                if nsession is not session:
                    node._session = session
                    nsession.unregister(node)
                    register(node)

    def send_action(self, action, content):
        """ Send an action to the client of this object.

        The action will only be sent if the object has a session.

        Parameters
        ----------
        action : str
            The name of the action performed.

        content : dict
            The content data for the action.

        """
        session = self._session
        if session is not None:
            session.send(self.object_id, action, content)

    def receive_action(self, action, content):
        """ Receive an action from the client of this messenger.

        The default implementation will dynamically dispatch the message
        to specially named handlers. Subclasses may reimplement this
        method if more control is required.

        Parameters
        ----------
        action : str
            The name of the action to perform.

        content : dict
            The content data for the action.

        """
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

