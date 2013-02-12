#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import deque
import logging
import re

from atom.api import (
    Atom, Observable, Str, Value, Constant, Enum, OwnerValue, ReadOnly,
)

from enaml.utils import make_dispatcher, id_generator

logger = logging.getLogger(__name__)


#: The dispatch function for action dispatching.
dispatch_action = make_dispatcher('on_action_', logger)


#: The identifier generator for object instances.
object_id_generator = id_generator('o_')


class ParentEvent(Atom):
    """ An object representing a change to an object's parent.

    User code should not create these event objects directly.

    """
    #: The old parent of the object, or None.
    old = ReadOnly()

    #: The new parent of the object, or None.
    new = ReadOnly()


class ChildEvent(Atom):
    """ An object representing a change to an object's children.

    User code should not create these event objects directly.

    """
    #: The list of old children of the object.
    old = ReadOnly()

    #: The list new children of the object.
    new = ReadOnly()


class ChildContext(Atom):
    """ A context manager which will emit a child event on an Object.

    This context manager will automatically emit the child event on an
    Object when the context is exited. This context manager can also be
    safetly nested; only the top-level context for a given object will
    emit the child event, effectively collapsing all transient state.

    """
    #: A reference to the owner of the children.
    owner = Value()

    #: A copy of the list of the owner's children.
    children = Value()

    #: A counter indicating the level of nesting of the context.
    count = Value(0)

    def __init__(self, owner):
        """ Initialize a ChildrenEventContext.

        Parameters
        ----------
        parent : Object or None
            The Object on which to emit a child event on context exit.
            To make it easier for reparenting operations, the parent
            can be None.

        """
        self.owner = owner

    def __enter__(self):
        if self.owner is not None and self.count == 0:
            self.children = self.owner._children[:]
            self.count += 1

    def __exit__(self, exc_type, exc_value, traceback):
        self.count -= 1
        if self.count == 0:
            owner = self.owner
            del owner.child_context
            if exc_type is None and owner is not None:
                old = self.children
                new = owner._children
                if old != new:
                    evt = ChildEvent.create(old=old, new=new)
                    owner.child_event(evt)


class Object(Observable):
    """ The most base class of the Enaml object hierarchy.

    An Enaml Object provides supports parent-children relationships and
    provides facilities for initializing, navigating, searching, and
    destroying the tree. It also contains methods for sending messages
    between objects when the object is part of a session.

    """
    #: An optional name to give to this object to assist in finding it
    #: in the tree (see . the 'find' method. There is no guarantee of
    #: uniqueness for an object `name`. It is left to the developer to
    #: choose an appropriate name.
    name = Str()

    #: A read-only property which returns the object's parent. This
    #: will be an instance Object or None if there is no parent.
    parent = property(lambda self: self._parent)

    #: A read-only property which returns the objects children. This is
    #: a list of Object instances. User code should not modify the list
    #: directly. Use the methods `set_parent` and `insert_children`.
    children = property(lambda self: self._children)

    #: A context which can be entered before modifying the children in
    #: order to collapse the children multiple children events.
    child_context = OwnerValue(factory=ChildContext)

    #: An event fired when an object is being destroyed. This event
    #: is fired once during the object lifetime, just before the
    #: object is removed from the tree structure.
    #destroyed = EnamlEvent

    #: A constant value which is the object's unique identifier. The
    #: identifier is guaranteed to be unique for the current process.
    object_id = Constant(factory=object_id_generator.next)

    #: The current lifetime state of the object. This should not be
    #: manipulated by user code.
    state = Enum('default', 'destroying', 'destroyed')

    #: A read-only property which is True if the object is destroying.
    is_destroying = property(lambda self: self.state == 'destroying')

    #: A read-only property which is True if the object is destroyed.
    is_destroyed = property(lambda self: self.state == 'destroyed')

    #: Private storage values. These should *never* be manipulated by
    #: user code. For performance reasons, these are not type checked.
    _parent = Value()                   # Object or None
    _children = Value(factory=list)     # list of Object

    def __init__(self, parent=None, **kwargs):
        """ Initialize an Object.

        Parameters
        ----------
        parent : Object or None, optional
            The Object instance which is the parent of this object, or
            None if the object has no parent. Defaults to None.

        **kwargs
            Additional keyword arguments to apply as attributes to the
            object after the parent has been set.

        """
        super(Object, self).__init__()
        if parent is not None:
            self.set_parent(parent)
        if kwargs:
            for key, value in kwargs.iteritems():
                setattr(self, key, value)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def destroy(self):
        """ Destroy this object and all of its children recursively.

        This will emit the `destroyed` event before any change to the
        object tree is made. After this returns, the object should be
        considered invalid and should no longer be used.

        """
        self.state = 'destroying'
        #self.destroyed()
        if len(self._children) > 0:
            for child in self._children:
                child.destroy()
            del self._children
        parent = self._parent
        if parent is not None:
            if parent.is_destroying:
                self._parent = None
            else:
                self.set_parent(None)
        self.state = 'destroyed'

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
        event = ParentEvent.create(old=old_parent, new=parent)
        self.parent_event(event)
        if old_parent is not None:
            with old_parent.child_context:
                old_parent._children.remove(self)
        if parent is not None:
            with parent.child_context:
                parent._children.append(self)

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
        insert_list = list(insert)
        insert_set = set(insert_list)
        if self in insert_set:
            raise ValueError('cannot use `self` as Object child')
        if len(insert_list) != len(insert_set):
            raise ValueError('cannot insert duplicate children')
        if not all(isinstance(child, Object) for child in insert_list):
            raise TypeError('children must be an Object instances')

        new = []
        added = False
        for child in self._children:
            if child in insert_set:
                continue
            if child is before:
                new.extend(insert_list)
                added = True
            new.append(child)
        if not added:
            new.extend(insert_list)

        for child in insert_list:
            old_parent = child._parent
            if old_parent is not self:
                child._parent = self
                event = ParentEvent.create(old=old_parent, new=self)
                child.parent_event(event)
                if old_parent is not None:
                    with old_parent.child_context:
                        old_parent._children.remove(child)

        with self.child_context:
            self._children = new

    def parent_event(self, event):
        """ Handle a `ParentEvent` posted to this object.

        This event handler is called when the parent on the object has
        changed, but before the children of the new parent have been
        updated. Sublasses may reimplement this method as required.

        Parameters
        ----------
        event : ParentEvent
            The event for the parent change of this object.

        """
        pass

    def child_event(self, event):
        """ Handle a `ChildEvent` posted to this object.

        This event handler is called by the child context when the last
        nested context is exited. Sublasses may reimplement this method
        as required.

        Parameters
        ----------
        event : ChildEvent
            The event for the children change of this object.

        """
        pass

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

