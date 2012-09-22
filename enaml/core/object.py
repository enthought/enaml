#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import deque
import logging
import re

from traits.api import (
    HasStrictTraits, ReadOnly, Str, Property, WeakRef, List, Instance, Bool,
    Disallow,
)

from enaml.utils import id_generator

from .trait_types import EnamlEvent


class Object(HasStrictTraits):
    """ The most base class of the Enaml object hierarchy.

    An Enaml object provides the basic messaging facilities and support
    for establishing parent-child relationships. It also includes basic
    tree walking and searching support.

    """
    #: The default object id generator. This can be overridden in a
    #: subclass to provide custom unique messenger identifiers.
    object_id_generator = id_generator('o')

    #: A read-only attribute which holds the object id. By default, the
    #: id is *not* a uuid. This choice was made to reduce the size of 
    #: messages sent across the wire. For most messages, using a uuid
    #: would significantly increase their size. If true uniqueness is
    #: required, then the object id generator can be overridden.
    object_id = ReadOnly

    #: An optional name to give to this object to assist in finding it
    #: in the tree. See e.g. the 'find' method. Note that there is no 
    #: uniqueness guarantee associated with the object `name`. It is 
    #: left up to the developer to choose an appropriate name.
    name = Str

    #: A read-only property which returns the instance's class name.
    class_name = Property

    #: A read-only property which returns the names of the instances
    #: base classes, stopping at Declarative.
    base_names = Property

    #: A read-only property which returns the parent of this object.
    #: The internal reference to the parent is kept weakly.
    parent = Property(depends_on='_parent')

    #: The internal storage for the parent of this object.
    _parent = WeakRef('Object', allow_none=True)

    #: A read-only property which returns the tuple of children for
    #: this object.The list of children for this object. 
    children = Property(depends_on='_children[]')

    #: The internal storage for the list of children for this object.
    _children = List(Instance('Object'))

    #: An event fired when a child has been added to this object. The
    #: payload will be the child that was added.
    child_added = EnamlEvent

    #: An event fired when a child is removed from this object. The
    #: payload will be the child that was removed.
    child_removed = EnamlEvent

    def __init__(self, parent=None):
        """ Initialize an Object.

        Parameters
        ----------
        parent : Object or None, optional
            The Object instance which is the parent of this object, or 
            None if the object has no parent. Defaults to None.

        """
        super(Object, self).__init__()
        self.set_parent(parent)

    #--------------------------------------------------------------------------
    # Property Methods
    #--------------------------------------------------------------------------
    def _get_class_name(self):
        """ The getter for the 'class_name' property.

        This property getter returns the string name of the class for
        this instance.

        """
        return type(self).__name__

    def _get_base_names(self):
        """ The property getter for the 'base_names' attribute.

        This property getter returns the list of names for all base
        classes in the instance type's mro, starting with its current
        type and stopping with Object.

        """
        base_names = []
        for base in type(self).mro():
            base_names.append(base.__name__)
            if base is Object:
                break
        return base_names

    def _get_parent(self):
        """ The property getter for the 'parent' attribute.

        This property getter returns the parent of this object.

        """
        return self._parent

    def _get_children(self):
        """ The property getter for the 'children' attribute.

        This property getter returns a tuple of the object's children.

        """
        return tuple(self._children)

    #--------------------------------------------------------------------------
    # Parenting Methods
    #--------------------------------------------------------------------------
    def set_parent(self, parent):
        """ Set the parent for this object.

        Parameters
        ----------
        parent : Object, None
            The Object instance to use for the parent, or None if this
            object should be de-parented.

        """
        old_parent = self._parent
        if parent is old_parent or parent is self:
            return
        self._parent = parent
        if old_parent is not None:
            try:
                old_parent._children.remove(self)
            except ValueError:
                pass
            else:
                old_parent.child_removed(self)
        if parent is not None:
            parent._children.append(self)
            parent.child_added(self)

    #--------------------------------------------------------------------------
    # Messaging Methods
    #--------------------------------------------------------------------------
    def handle_action(self, action, content):
        """ Handle an action sent from the client of this messenger.

        This is called by the messenger's Session object when the client
        of the messenger sends it a message. The default behavior of the 
        method is to dispatch the message to a handler method named with
        the name 'on_action_<action>' where <action> is substituted with
        the message action.

        Parameters
        ----------
        action : str
            The action to be performed by the messenger.

        content : ObjectDict
            The content dictionary for the action.

        """
        handler_name = 'on_action_' + action
        handler = getattr(self, handler_name, None)
        if handler is not None:
            handler(content)
        else:
            # XXX probably want to raise an exception so the Session
            # can convert it into an error response.
            # XXX make this logging more configurable
            msg = "Unhandled action '%s' sent to messenger %s:%s"
            name = type(self.__name__)
            logging.warn(msg % (action, name, self.object_id))

    def send_action(self, action, content):
        """ Send an action to the client of this messenger.

        This method can be called to send an unsolicited message of
        type 'action' to the client of this messenger.

        Parameters
        ----------
        action : str
            The action for the message.

        content : dict
            The content of the message.

        """
        session = self.session
        if session is None:
            # XXX make this logging more configurable
            msg = 'No Session object for messenger %s:%s'
            name = type(self).__name__
            logging.warn(msg % (name, self.object_id))
        else:
            session.send_action(self.object_id, action, content)

    def snapshot(self):
        """ Create a snapshot of the tree starting from this object.

        Returns
        -------
        result : dict
            A snapshot of the object tree, from this object down.

        """
        snap = {}
        snap['object_id'] = self.object_id
        snap['class'] = self.class_name
        snap['bases'] = self.base_names
        snap['name'] = self.name
        snap['children'] = [c.snapshot() for c in self.snap_children()]
        return snap

    def snap_children(self):
        """ Get the children to include in the snapshot.

        This method is called to retrieve the children to include with
        the snapshot of the component. The default implementation just
        returns the tuple of `children`. Subclasses should reimplement
        this method if they need more control.

        Returns
        -------
        result : iterable
            An iterable of children to include in the component
            snapshot.

        """
        return self.children

    #--------------------------------------------------------------------------
    # Tree Methods
    #--------------------------------------------------------------------------
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

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    #: The HasTraits class defines a class attribute 'set' which is a 
    #: deprecated alias for the 'trait_set' method. The problem is that
    #: having that as an attribute interferes with the ability of Enaml 
    #: expressions to resolve the builtin 'set', since dynamic scoping
    #: takes precedence over builtins. This resets those ill-effects.
    set = Disallow

    _trait_change_notify_flag = Bool(True)
    def trait_set(self, trait_change_notify=True, **traits):
        """ An overridden HasTraits method which keeps track of the
        trait change notify flag.

        The default implementation of trait_set has side effects if a
        call to setattr(...) causes a recurse into trait_set in that
        the notification context of the original call will be reset.

        This reimplemented method will make sure that context is reset
        appropriately for each call. This is required for Enaml since
        bound attributes are lazily computed and set quitely on the fly. 

        A ticket has been filed against traits trunk:
            https://github.com/enthought/traits/issues/26
            
        """
        last = self._trait_change_notify_flag
        self._trait_change_notify_flag = trait_change_notify
        self._trait_change_notify(trait_change_notify)
        try:
            for name, value in traits.iteritems():
                setattr(self, name, value)
        finally:
            self._trait_change_notify_flag = last
            self._trait_change_notify(last)
        return self

