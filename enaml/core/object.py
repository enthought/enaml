#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from collections import defaultdict, deque, namedtuple
import logging
import re
from weakref import WeakValueDictionary

from traits.api import (
    HasStrictTraits, ReadOnly, Str, Property, Tuple, Instance, Bool, Disallow,
    cached_property
)

from enaml.utils import LoopbackGuard, id_generator

from .trait_types import EnamlEvent


logger = logging.getLogger(__name__)


class ActionPipeInterface(object):
    """ An abstract base class defining an action pipe interface.

    Concrete implementations of this interface can be used by Object
    instances to sent messages to their client objects.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def send(self, object_id, action, content):
        """ Send an action to the client of an object.

        Parameters
        ----------
        object_id : str
            The object id for the Object sending the message.

        action : str
            The action that should be take by the client object.

        content : dict
            The dictionary of content needed to perform the action.

        """
        raise NotImplementedError


#: A namedtuple which contains information about a child change event.
#: The `added` and `removed` slots will be sets of Objects which were
#: added and removed. The `current` slot will be a tuple of Objects.
#: Instances of this object are created by the ChildEventContext.
ChildEvent = namedtuple('ChildEvent', 'added removed current')


class ChildEventContext(object):
    """ A context manager which will emit a child event on an Object.

    This context manager will automatically emit the child event on an
    Object when the context is exited. This context manager can also be
    safetly nested; only the top-level context for a given object will
    emit the child event, effectively collapsing all transient state.

    """
    #: Class level storage for tracking nested context managers.
    _counters = defaultdict(int)

    def __init__(self, parent):
        """ Initialize a ChildEventContext.

        Parameters
        ----------
        parent : Object
            The Object on which to emit a child event on context exit.

        """
        self._parent = parent
        self._old = ()

    def __enter__(self):
        """ Enter the child event context.

        This method will snap the current child state of the parent and
        use it to diff the state on context exit.

        """
        parent = self._parent
        self._old = parent.children
        self._counters[parent] += 1

    def __exit__(self, exc_type, exc_value, traceback):
        """ Exit the child event context.

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
            if exc_type is None and parent.initialized:
                current = parent.children
                old_set = set(self._old)
                curr_set = set(current)
                removed = old_set - curr_set
                added = curr_set - old_set
                evt = ChildEvent(added, removed, current)
                parent.child_event(evt)


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
    class_name = Property(fget=lambda self: type(self).__name__)

    #: A read-only property which returns the names of the instances
    #: base classes, stopping at Declarative.
    base_names = Property

    #: A read-only property which returns the parent of this object.
    parent = Property(fget=lambda self: self._parent, depends_on='_parent')

    #: The internal storage for the parent of this object.
    _parent = Instance('Object')

    #: A read-only property which returns the tuple of children for
    #: this object.
    children = Property(depends_on='_children')

    #: The internal storage for the tuple of children for this object.
    _children = Tuple

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

    #: A pipe interface to use for sending messages by the object. If
    #: the pipe is None the object will walk up the ancestor tree in
    #: order to find a pipe to use. To silence an object, set this
    #: attribute to a null pipe interface.
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
    # Private API
    #--------------------------------------------------------------------------
    def _destroy(self, notify):
        """ The private destructor implementation.

        This method ensures that only the top-level object notifies the
        client of the destruction. The destruction of all children of
        an object is implicit and reduces the number of messages which
        must be sent to the client.

        Parameters
        ----------
        notify : bool
            Whether to send the 'destroy' action to the client.

        """
        if notify:
            self.send_action('destroy', {})
        self.initialized = False
        parent = self._parent
        if parent is not None:
            if parent.initialized:
                self.set_parent(None)
            else:
                self._parent = None
        children = self._children
        self._children = ()
        for child in children:
            child._destroy(False)

    #--------------------------------------------------------------------------
    # Property Methods
    #--------------------------------------------------------------------------
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

    @cached_property
    def _get_children(self):
        """ The property getter for the 'children' attribute.

        This property getter returns a tuple of the object's children.

        """
        return self._children

    #--------------------------------------------------------------------------
    # Initialization Methods
    #--------------------------------------------------------------------------
    def initialize(self):
        """ A method called by the external user of the object tree.

        This method should only be called after the entire object tree
        is built, but before it is put in use for message passing. This
        method performs a bottom-up traversal of the object tree, so it
        need only be called on the top-level object. This method should
        only be called once. Multiple calls to this method are ignored.

        """
        # Note: the body of this method is highly sensitive to order.
        # be sure all side effects are understood before modifying.
        if self.initialized:
            return

        # Refresh the pipe before initializing the children, so that
        # when they do the same, the only have to hop 1 time at max.
        self.inherit_pipe()
        for child in self._children:
            child.initialize()

        # This event may cause arbitrary side effects. A good example is
        # the Include type, which will possibly add a bunch of children
        # to its parent as a result. This means a bunch of trait change
        # notification may be run. Only bind the change handlers after
        # the event has quieted down.
        self.init()
        self.bind()
        self.initialized = True

    def bind(self):
        """ A method called at the end of initialization.

        The intent of this method is to allow a widget to hook up its
        trait change notification handlers which will be responsible
        for sending actions. The default implementation is a no-op.

        """
        pass

    def destroy(self):
        """ Explicity destroy this object and all of its children.

        This method sends the 'destroy' action to the client, sets the
        `intialized` flag to False, sets the parent reference to None,
        sets the children to an empty tuple, then destroys the children.

        """
        self._destroy(True)

    #--------------------------------------------------------------------------
    # Parenting Methods
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

        """
        old_parent = self._parent
        if parent is old_parent:
            return

        if parent is self:
            raise ValueError('Cannot use `self` as Object parent')

        self._parent = parent
        if old_parent is not None:
            old_kids = old_parent._children
            idx = old_kids.index(self)
            old_kids = old_kids[:idx] + old_kids[idx + 1:]
            with ChildEventContext(old_parent):
                old_parent._children = old_kids

        if parent is not None:
            with ChildEventContext(parent):
                parent._children = parent._children + (self,)
                # Initialize the child from within the child event
                # context since it may have arbitrary side effects,
                # including adding more children to its parent.
                if parent.initialized:
                    self.initialize()

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

        """
        insert_tup = tuple(insert)
        insert_set = set(insert_tup)
        if self in insert_set:
            raise ValueError('Cannot use `self` as Object child')
        if len(insert_tup) != len(insert_set):
            raise ValueError('Cannot have duplicate children')

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
                if old_parent is not None:
                    old_kids = old_parent._children
                    idx = old_kids.index(child)
                    old_kids = old_kids[:idx] + old_kids[idx + 1:]
                    with ChildEventContext(old_parent):
                        old_parent._children = old_kids

        with ChildEventContext(self):
            self._children = tuple(new)
            if self.initialized:
                # Initialize the children from within the child event
                # context since they may have arbitrary side effects,
                # including adding more children to their parent.
                for child in insert_tup:
                    child.initialize()

    def remove_children(self, remove, destroy=True):
        """ Remove the given children from this object.

        The given children will be removed from the children of this
        object and their parent will be set to None. Any given child
        which is not a child of this object will be ignored.

        Parameters
        ----------
        remove : iterable
            An iterable of Object children to remove from this object.

        destroy : bool, optional
            Whether or not to destroy the removed children. The default
            is True.

        """
        old = []
        new = []
        remove_set = set(remove)
        for child in self._children:
            if child in remove_set:
                old.append(child)
            else:
                new.append(child)

        for child in old:
            child._parent = None

        with ChildEventContext(self):
            self._children = tuple(new)

        if destroy:
            for child in old:
                child.destroy()

    def replace_children(self, remove, before, insert, destroy=True):
        """ Perform an 'atomic' remove and insert children operation.

        This method can be used to combine a remove and insert child
        operation into a transactions which will emit only a single
        child event. This will be more efficient than calling the
        `remove_children` method followed by `insert_children`.

        Parameters
        ----------
        remove : iterable
            An iterable of Object children to remove from this object.

        before : Object or None
            A child object to use as the marker for inserting the new
            children. The new children will be inserted directly before
            this marker. If the Object is None or not a child, then the
            new children will be added to the end of the children.

        insert : iterable
            An iterable of Object children to insert into this object.

        destroy : bool, optional
            Whether or not to destroy the removed children. The default
            is True.

        """
        remove_tup = tuple(remove)
        insert_tup = tuple(insert)
        remove_set = set(remove_tup)
        insert_set = set(insert_tup)
        if self in insert_set:
            raise ValueError('Cannot use `self` as Object child')
        if len(insert_tup) != len(insert_set):
            raise ValueError('Cannot have duplicate children')

        old = []
        new = []
        added = False
        for child in self._children:
            if child in remove_set:
                if child not in insert_set:
                    old.append(child)
                continue
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
                if old_parent is not None:
                    old_kids = old_parent._children
                    idx = old_kids.index(child)
                    old_kids = old_kids[:idx] + old_kids[idx + 1:]
                    with ChildEventContext(old_parent):
                        old_parent._children = old_kids

        for child in old:
            child._parent = None

        with ChildEventContext(self):
            self._children = tuple(new)
            if self.initialized:
                # Initialize the children from within the child event
                # context since they may have arbitrary side effects,
                # including adding more children to their parent.
                for child in insert_tup:
                    child.initialize()

        if destroy:
            for child in old:
                child.destroy()

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
            msg = "Unhandled action '%s' for Object %s:%s"
            logger.warn(msg % (action, self.class_name, self.object_id))

    def inherit_pipe(self):
        """ Inherit the action pipe from the ancestors of this object.

        If the `action_pipe` for this instance is None, then this method
        will walk the tree of ancestors until it finds an object with a
        non null `action_pipe`. That pipe will then be used as the pipe
        for this object.

        """
        if self.action_pipe is None:
            parent = self._parent
            while parent is not None:
                pipe = parent.action_pipe
                if pipe is not None:
                    self.action_pipe = pipe
                    return
                parent = parent._parent

    def send_action(self, action, content):
        """ Send an action on the action pipe for this object.

        The action will only be sent if the object is fully initialized.

        Parameters
        ----------
        action : str
            The name of the action performed.

        content : dict
            The content data for the action.

        """
        if self.initialized:
            pipe = self.action_pipe
            if pipe is None:
                self.inherit_pipe()
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

    def child_event(self, event):
        """ Handle a `ChildEvent` posted to this object.

        This event handler is called by a `ChildEventContext` when the
        children have changed for this object. It is called *after* the
        trait change notifications for `children` have fired and *after*
        all child initialization is complete. It is only called if the
        object is fully initialized. The default implementation of this
        method sends a `children_changed` action to the client. If a
        subclass requires more control, it may reimplement this method.

        Parameters
        ----------
        event : ChildEvent
            The child event for the children change of this object.

        """
        content = {}
        added = event.added
        removed = event.removed
        current = event.current
        # XXX i'm not fond of these snappable checks
        content['order'] = [c.object_id for c in current if c.snappable]
        content['removed'] = [c.object_id for c in removed if c.snappable]
        content['added'] = [c.snapshot() for c in added if c.snappable]
        self.send_action('children_changed', content)

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

