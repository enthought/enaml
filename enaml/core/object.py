#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from collections import deque
import logging
import re
from weakref import WeakValueDictionary

from traits.api import (
    HasStrictTraits, ReadOnly, Str, Property, Tuple, Instance, Bool, Disallow, 
    cached_property
)

from enaml.utils import LoopbackGuard, id_generator

from .trait_types import EnamlEvent


class ActionPipeInterface(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def send(self, object_id, action, content):
        raise NotImplementedError


class Object(HasStrictTraits):
    """ The most base class of the Enaml object hierarchy.

    An Enaml object provides the basic messaging facilities and support
    for establishing parent-child relationships. It also includes basic
    tree walking and searching support.

    """
    #: The class level object id generator. This can be overridden 
    #: in a subclass to provide custom unique messenger identifiers.
    object_id_generator = id_generator('o_')

    #: A read-only attribute which holds the object id. By default, the
    #: id is *not* a uuid. This choice was made to reduce the size of 
    #: messages sent across the wire. For most messages, using a uuid
    #: would significantly increase their size. If true uniqueness is
    #: required, then the object id generator can be overridden.
    object_id = ReadOnly

    #: A backwards compatibility alias for `object_id`. New code should
    #: access `object_id` directly.
    widget_id = Property(fget=lambda self: self.object_id)

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
    parent = Property(depends_on='_parent')

    #: The internal storage for the parent of this object.
    _parent = Instance('Object')

    #: A read-only property which returns the tuple of children for
    #: this object.The list of children for this object. 
    children = Property(depends_on='_children')

    #: The internal storage for the tuple of children for this object.
    _children = Tuple

    #: A boolean flag indicating whether this object allows children.
    #: If the flag is False, then attempting to use this object as the
    #: parent of another object will raise an exception. The default
    #: behavior is to allow children.
    allow_children = Bool(True)

    #: A boolean flag indicating whether this object is snappable. Only
    #: snappable objects are included in the `children` field of their
    #: their parent's snapshot. Objects are snappable by default.
    snappable = Bool(True)

    #: An event fired during the initialization pass. This allows any 
    #: listeners to perform work which depends on the object tree being
    #: in a complete and stable state.
    init = EnamlEvent

    #: A boolean flag which indicates whether this Object instance has
    #: been initialized. This is set to True after the `init` event is
    #: fired. It should not be manipulated by user code.
    initialized = Bool(False)

    #: A signal emitted when an action has been taken by the object that
    #: may be of interest to external listeners. The payload will be the
    #: object id, the action name, and the content dict.
    action_pipe = Instance(ActionPipeInterface)

    #: A loopback guard which can be used to prevent a signal loopback 
    #: cycle when setting attributes from within an action handler.
    loopback_guard = Instance(LoopbackGuard, ())

    #: Class level storage for Object instances. Objects are added to
    #: this dict as they are created. The instances are stored weakly.
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
        result : Object or None
            The Object for given identifier, or None if no object
            is found.

        """
        return cls._objects.get(object_id)

    def __new__(cls, *args, **kwargs):
        """ Create a new Object.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            the object.

        """
        self = super(Object, cls).__new__(cls)
        object_id = cls.object_id_generator.next()
        objects = cls._objects
        if object_id in objects:
            raise ValueError('Duplicate object id `%s`' % object_id)
        self.object_id = object_id
        objects[object_id] = self
        return self

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

    @cached_property
    def _get_children(self):
        """ The property getter for the 'children' attribute.

        This property getter returns a tuple of the object's children.

        """
        return self._children

    #--------------------------------------------------------------------------
    # Initialization Methods
    #--------------------------------------------------------------------------
    def initialize(self, pipe_interface=None):
        """ A method called by the external user of the object tree.

        This method should only be called after the entire object tree
        is built, but before it is put in use for message passing. This
        method performs a bottom-up traversal of the object tree, so it
        need only be called on the top-level object. This method should
        only be called once. Multiple calls to this method are ignored.

        Parameters
        ----------
        pipe : ActionPipeInterface, optional
            An optional action pipe interface for objects in this tree
            to use for sending messages action messages.

        """
        if self.initialized:
            return
        for child in self._children:
            child.initialize(pipe_interface)
        self.init()
        self.initialized = True
        self.bind()
        self.action_pipe = pipe_interface

    def bind(self):
        """ A method called at the end of initialization.

        The intent of this method is to allow a widget to hook up its
        trait change notification handlers which will be responsible 
        for sending actions. The default implementation is a no-op.

        """
        pass

    def destroy(self):
        """ Explicity destroy this object and all of its children.

        This method sets the `intialized` flag to False, sets the parent 
        reference to None, destroys all of the children, and then sets
        the children reference to an empty tuple. This will break the 
        explicit reference cycles introduced by Object.

        """
        self.initialized = False
        if self._parent is not None:
            if self._parent.initialized:
                self.set_parent(None)
            else:
                self._parent = None
        for child in self._children:
            child.destroy()
        self._children = ()
        self.send_action('destroy', {})

    #--------------------------------------------------------------------------
    # Parenting Methods
    #--------------------------------------------------------------------------
    def set_parent(self, parent):
        """ Set the parent for this object.

        If the parent is not None, the child will be appended to the end
        of the parent's children. If the parent is already the parent of
        this object, then this method is a no-op.

        Parameters
        ----------
        parent : Object or None
            The Object instance to use for the parent, or None if this
            object should be de-parented.

        """
        old_parent = self._parent
        if parent is old_parent:
            return

        if parent is not None and not parent.allow_children:
            msg = 'Parent Object `%s` does not allow children'
            raise ValueError(msg % parent)
        if parent is self:
            raise ValueError('Cannot use `self` as Object parent')

        self._parent = parent
        if old_parent is not None:
            children = old_parent._children
            try:
                idx = children.index(self)
            except ValueError:
                pass
            else:
                old_parent._children = children[:idx] + children[idx+1:]

        if parent is not None:
            parent._children += (self,)

    def insert_children(self, index, children):
        """ Insert children into this object at the given index. 

        The children will be automatically parented and inserted into
        the tuple of children. If any children are already children of
        this object, then they will be moved to the appropriate index.

        Parameters
        ----------
        children : iterable of Object
            The children to add to this object.

        """
        if not self.allow_children:
            msg = 'Parent Object `%s` does not allow children'
            raise ValueError(msg % self)
        
        children = list(children)
        children_set = set(children)

        if self in children_set:
            raise ValueError('Cannot use `self` as Object child')
        if len(children) != len(children_set):
            raise ValueError('Cannot have duplicate children')

        for child in children:
            old_parent = child._parent
            if old_parent is not self:
                child._parent = self
                if old_parent is not None:
                    okids = old_parent._children
                    try:
                        idx = okids.index(child)
                    except ValueError:
                        pass
                    else:
                        old_parent._children = okids[:idx] + okids[idx+1:]

        curr = [c for c in self._children if c not in children_set]
        new = tuple(curr[:index]) + tuple(children) + tuple(curr[index:])
        self._children = new

    def _children_changed(self, old, new):
        """ A change handler invoked when the tuple of children changes.

        If the object is fully initialized, then the `action` signal 
        will be emitted with a `children_changed` action.

        """
        if self.initialized:
            # Old can sometimes be None due to `cached_property` oddities
            old = old or ()
            old_set = set(old)
            new_set = set(new)
            removed = old_set - new_set
            added = new_set - old_set
            content = {}
            content['order'] = [c.object_id for c in new if c.snappable]
            content['removed'] = [c.object_id for c in removed if c.snappable]
            content['added'] = [c.snapshot() for c in added if c.snappable]
            self.send_action('children_changed', content)

    #--------------------------------------------------------------------------
    # Messaging Methods
    #--------------------------------------------------------------------------
    def handle_action(self, action, content):
        """ Handle the specified action with the given content.

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
            # XXX make this logging more configurable
            msg = "Unhandled action '%s' for Object %s:%s"
            logging.warn(msg % (action, self.class_name, self.object_id))

    def send_action(self, action, content):
        """ Send an action on the action pipe for this object.

        Parameters
        ----------
        action : str
            The name of the action performed.

        content : dict
            The content data for the action.

        """
        pipe = self.action_pipe
        if pipe is not None:
            pipe.send(self.object_id, action, content)

    def snapshot(self):
        """ Create a snapshot of the tree starting from this object.

        Parameters
        ----------
        child_filter : callable, optional
            An optional filter func to limit the children which are
            included in the snapshot. The default is None indicates
            that all children are included in the snapshot.

        Returns
        -------
        result : dict
            A snapshot of the object tree, from this object down.

        """
        snap = {}
        snap['object_id'] = self.object_id
        snap['widget_id'] = self.widget_id # backwards compatibility
        snap['class'] = self.class_name
        snap['bases'] = self.base_names
        snap['name'] = self.name
        snap['children'] = [c.snapshot() for c in self.snap_children()]
        return snap

    def snap_children(self):
        """ Get the children to include in the snapshot.

        This method is called to retrieve the children to include with
        the snapshot of the component. The default implementation just
        returns the `children` of this object whose `snappable` method
        returns True. Subclasses should reimplement this method if they
        need more control.

        Returns
        -------
        result : iterable
            An iterable of children to include in the object snapshot.

        """
        return [child for child in self._children if child.snappable]

    def publish_attributes(self, *attrs):
        """ A convenience method provided for subclasses to use to 
        publish changes to attributes as actions performed.

        The action name is created by prefixing 'set_' to the name of
        the changed attribute. This method is suitable for most cases
        of simple attribute publishing. More complex cases will need
        to implement their own dispatching handlers. The handler for
        the changes will only emit the `action` signal if the attribute
        name is not held by the loopback guard.

        Parameters
        ----------
        *attrs
            The string names of the attributes to publish to the client.
            The values of these attributes should be JSON serializable. 
            More complex values should use their own dispatch handlers.

        """
        otc = self.on_trait_change
        handler = self._publish_attr_handler
        for attr in attrs:
            otc(handler, attr)

    def set_guarded(self, **attrs):
        """ A convenience method provided for subclasses to set a
        sequence of attributes from within a loopback guard.

        Parameters
        ----------
        **attrs
            The attributes which should be set on the object from
            within a loopback guard context.

        """
        with self.loopback_guard(*attrs):
            for name, value in attrs.iteritems():
                setattr(self, name, value)

    def _publish_attr_handler(self, name, new):
        """ A private handler which will emit the `action` signal in
        response to a trait change event.

        The action will be created by prefixing the attribute name with
        'set_'. The value of the attribute should be JSON serializable.
        The content of the message will have the name of the attribute 
        as a key, and the value as its value. If the loopback guard is 
        held for the given name, then the signal will not be emitted,
        helping to avoid potential loopbacks.

        """
        if name not in self.loopback_guard:
            action = 'set_' + name
            content = {name: new}
            self.send_action(action, content)

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

