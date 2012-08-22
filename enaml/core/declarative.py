#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import deque
import re

from traits.api import (
    HasStrictTraits, Instance, List, Property, Str, Dict, Disallow, Bool,
    Undefined
)

from .expressions import AbstractExpression
from .operator_context import OperatorContext
from .trait_types import EnamlEvent, ExpressionTrait, UserAttribute, UserEvent


#: The traits types on an Declarative instance which can be overridden
#: by the user in an enamldef declaration.
_OVERRIDE_ALLOWED = (UserAttribute, UserEvent)


class Declarative(HasStrictTraits):
    """ The most base class of the Enaml component hierarchy.

    This class provides the core functionality required of declarative
    Enaml types. It can be used directly in an Enaml component tree
    to store and react to state changes just like any other component.
    However, it has no concept of visual representation or client
    communication. That functionality is added by subclasses.

    """
    #: An optional name to give to this component to assist in finding
    #: it in the tree. See e.g. the 'find' method.
    name = Str

    #: A readonly property which returns the instance's class name.
    class_name = Property(fget=lambda self: type(self).__name__)

    #: A readonly property which returns the names of the instances
    #: base classes, stopping at Declarative.
    base_names = Property

    #: A readonly property which returns the current instance of the
    #: component. This allows declarative Enaml expressions to access
    #: 'self' according to Enaml's dynamic scoping rules.
    self = Property(fget=lambda self: self)

    #: The parent component of this component. It is stored internally
    #: as a weakref to mitigate issues with reference cycles. 
    #: XXX store these strongly for now, traits gets notification
    #: errors on shutdown when the weakrefs die. grr....
    parent = Instance('Declarative', allow_none=True)

    #: The list of children for this component. 
    children = List(Instance('Declarative'))

    #: An event emitted when the list of children for this component
    #: changes, either in whole or in place. The payload of the event
    #: is a dict with the keys 'added' and 'removed' which are lists
    #: of the children removed and added, respectively. This event is
    #: emitted once all reparenting operations for all of the children
    #: are complete.
    children_changed = EnamlEvent

    #: manipulated by user code.
    initialized = Bool(False)

    #: An event fired during the post init traversal. This allows 
    #: any declarative bindings to perform any necessary procedural
    #: initialization, such as initializing dynamic children.
    inited = EnamlEvent

    #: The private dictionary of expression objects that are bound to 
    #: attributes on this component. It should not be manipulated by
    #: user code. Rather, expressions should be bound by the operators
    #: by calling the '_bind_expression' method.
    _expressions = Dict(Str, List(Instance(AbstractExpression)))

    #: A class attribute used by the Enaml compiler machinery to store
    #: the builder functions on the class. The functions are called
    #: when a component is instantiated and are the mechanism by which
    #: a component is populated with its declarative children and bound
    #: expression objects.
    _builders = []

    #: The HasTraits class defines a class attribute 'set' which is
    #: a deprecated alias for the 'trait_set' method. The problem
    #: is that having that as an attribute interferes with the 
    #: ability of Enaml expressions to resolve the builtin 'set',
    #: since the dynamic attribute scoping takes precedence over
    #: builtins. This resets those ill-effects.
    set = Disallow

    def __init__(self, parent=None, **kwargs):
        """ Initialize a declarative component.

        Parameters
        ----------
        parent : Declarative or None, optional
            The Declarative component instance which is the parent of 
            this component, or None if the component has no parent.
            Defaults to None.

        **kwargs
            Any other positional arguments needed to initialize the
            component.

        """
        super(Declarative, self).__init__()
        # Set the parent reference on the object. We do this quietly
        # so that the _parent_changed handler is not invoked. This 
        # saves us a linear scan over the parent's children since we
        # can be reasonably sure that this child has not yet been
        # added as a child of the parent.
        if parent is not None:
            self.trait_setq(parent=parent)
            parent.children.append(self)

        # If any builders are present, they need to be invoked before
        # applying any other keyword arguments so that bound expressions
        # do not override the keywords. The builders appear and are run
        # in the reverse order of a typical mro. The most base builder
        # gets to add its children and bind its expressions first. 
        # Builders that come later can then override these bindings.
        # Each component gets it's own identifier namespace and current
        # operator context.
        if self._builders:
            identifiers = {}
            operators = OperatorContext.active_context()
            for builder in self._builders:
                builder(self, identifiers, operators)

        # We apply the keyword arguments after the rest of the tree is
        # is created. This makes sure that parameters passed in by the
        # user are not overridden by default expression bindings.
        self.trait_set(**kwargs)

        # If this widget is top level, then the a bottom-up traversal
        # is performed to fire off the initialization events.
        if parent is None:
            self._post_init_traverse()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @classmethod
    def _add_user_attribute(cls, name, attr_type, is_event):
        """ A private classmethod used by the Enaml compiler machinery.

        This method is used to add user attributes and events to custom
        derived enamldef components. If the attribute already exists on 
        the class and is not a user defined attribute, then an exception
        will be raised. The only method of overriding standard trait 
        attributes is through traditional subclassing.

        Parameters
        ----------
        name : str
            The name of the attribute to add to the class.

        attr_type : type
            The type of the attribute.

        is_event : bool
            True if the attribute should be a UserEvent, False if it
            should be a UserAttribute.

        """
        base_traits = cls.__base_traits__
        if name in base_traits:
            ttype = base_traits[name].trait_type
            if not isinstance(ttype, _OVERRIDE_ALLOWED):
                msg = ("can't add '%s' attribute. The '%s' attribute on "
                       "enamldef '%s.%s' already exists.")
                items = (name, name, cls.__module__, cls.__name__)
                raise TypeError(msg % items)

        trait_attr_cls = UserEvent if is_event else UserAttribute
        try:
            user_trait = trait_attr_cls(attr_type)
        except TypeError:
            msg = ("'%s' is not a valid type for the '%s' attribute "
                   "declaration on enamldef '%s.%s'")
            items = (attr_type, name, cls.__module__, cls.__name__)
            raise TypeError(msg % items)

        # XXX HasTraits.add_class_trait will raise an exception if the
        # the trait is already defined. There does not appear to be a
        # way to turn this off, nor does there appear to be a way to 
        # formally remove a class trait. So, we just do what the traits
        # metaclass does when adding traits and directly add the ctrait 
        # to the appropriate class dictionaries. The add_class_trait
        # classmethod does some extra work to make sure that the trait
        # is added to all subclasses, but that does not appear to be
        # needed in this case, since this method will only be called by
        # the compiler machinery for brand new subclasses.
        ctrait = user_trait.as_ctrait()
        cls.__base_traits__[name] = ctrait
        cls.__class_traits__[name] = ctrait

    def _post_init_traverse(self):
        """ A method called when the top level widget if fully inited.

        This method performs a bottom up traversal of the tree, flips
        the `initialized` flag, and fires off the `inited` event.

        """ 
        for child in self.children:
            child._post_init_traverse()
        self.initialized = True
        self.inited()

    def _bind_expression(self, name, expression, notify_only=False):
        """ A private method used by the Enaml execution engine.

        This method is called by the Enaml operators to bind the given
        expression object to the given attribute name. If the attribute
        does not exist, an exception is raised. A strong reference to 
        the expression object is kept internally.

        Parameters
        ----------
        name : string
            The name of the attribute on which to bind the expression.
        
        expression : AbstractExpression
            A concrete implementation of AbstractExpression.
        
        notify_only : bool, optional
            If True, the expression is only a notifier, in which case
            multiple binding is allowed, otherwise the new expression
            overrides any old non-notify expression. Defaults to False.

        """
        curr = self.trait(name)
        if curr is None or curr.trait_type is Disallow:
            msg = "Cannot bind expression. %s object has no attribute '%s'"
            raise AttributeError(msg % (self, name))

        # If this is the first time an expression is being bound to the
        # given attribute, then we hook up a change handler. This ensures
        # that we only get one notification event per bound attribute.
        # We also create the notification entry in the dict, which is 
        # a list with at least one item. The first item will always be
        # the left associative expression (or None) and all following
        # items will be the notify_only expressions.
        expressions = self._expressions
        if name not in expressions:
            self.on_trait_change(self._on_bound_attr_changed, name)
            expressions[name] = [None]

        # There can be multiple notify_only expressions bound to a 
        # single attribute, so they just get appended to the end of
        # the list. Otherwise, the left associative expression gets
        # placed at the zero position of the list, overriding any
        # existing expression.
        if notify_only:
            expressions[name].append(expression)
        else:
            handler = self._on_expression_changed
            old = expressions[name][0]
            if old is not None:
                old.expression_changed.disconnect(handler)
            expression.expression_changed.connect(handler)
            expressions[name][0] = expression
            
            # Hookup support for default value computation. We only need
            # to add an ExpressionTrait once, since it will reach back 
            # into the _expressions dict as needed and retrieve the most
            # current bound expression.
            if not isinstance(curr.trait_type, ExpressionTrait):
                self.add_trait(name, ExpressionTrait(curr))

    def _parent_changed(self, old, new):
        """ The change handler for the 'parent' attribute. 

        This handler ensures that the child is properly removed from 
        the children of its old parent.

        """
        # The old parent will be undefined if it was garbage collected.
        if old is not None and old is not Undefined:
            if self in old.children:
                old.children.remove(self)
        if new is not None:
            if self not in new.children:
                new.children.append(self)

    def _children_changed(self, old, new):
        """ The change handler for the 'children' attribute.

        This handler will be called when the list changes as a whole. 
        Children in the old list which are not in the new list, with
        'self' as their parent will be de-parented. Children in the 
        new list with an improper parent will be properly parented.
        The 'children_changed' event will be fired when the parenting
        operations are complete.

        """
        added = []
        removed = []
        push_added = added.append
        push_removed = removed.append
        old_set = set(old)
        new_set = set(new)
        for child in old:
            if child not in new_set:
                push_removed(child)
                if child.parent is self:
                    child.parent = None
        for child in new:
            if child not in old_set:
                push_added(child)
                if child.parent is not self:
                    child.parent = self
        self.children_changed({'added': added, 'removed': removed})

    def _children_items_changed(self, items_evt):
        """ The change handler for the 'children' attribute.

        This handler will be called when the items in the list change. 
        Children that were added will be properly parented. Children 
        that were removed will be unparented. The 'children_changed' 
        event will be fired when the parenting operations are complete.

        """
        added = []
        removed = []
        push_added = added.append
        push_removed = removed.append
        old_set = set(items_evt.removed)
        new_set = set(items_evt.added)
        for child in items_evt.removed:
            if child not in new_set:
                push_removed(child)
                if child.parent is self:
                    child.parent = None
        for child in items_evt.added:
            if child not in old_set:
                push_added(child)
                if child.parent is not self:
                    child.parent = self
        self.children_changed({'added': added, 'removed': removed})
        
    def _get_base_names(self):
        """ The property getter for the 'base_names' attribute.

        This property getter returns the list of names for all base
        classes in the instance type's mro, starting with its current
        type and stopping with Declarative.

        """
        base_names = []
        for base in type(self).mro():
            base_names.append(base.__name__)
            if base is Declarative:
                break
        return base_names
        
    def _on_expression_changed(self, expression, name, value):
        """ A private signal callback for the expression_changed signal
        of the bound expressions. It updates the value of the attribute
        with the new value from the expression.

        """
        setattr(self, name, value)
    
    def _on_bound_attr_changed(self, obj, name, old, new):
        """ A private handler which is called when any attribute which
        has a bound signal changes. It calls the notify method on each
        of the expressions bound to that attribute, but if the component
        is marked as live.

        """
        # The check for None is for the case where there are no left 
        # associative expressions bound to the attribute, so the first
        # entry in the list is still None.
        for expr in self._expressions[name]:
            if expr is not None:
                expr.notify(old, new)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Create a snapshot of the tree starting from this component.

        Returns
        -------
        result : dict
            A dictionary snapshot of the declarative component tree, 
            from this component downward.

        """
        snap = {}
        snap['class'] = self.class_name
        snap['bases'] = self.base_names
        snap['name'] = self.name
        snap['children'] = [c.snapshot() for c in self.snap_children()]
        return snap

    def snap_children(self):
        """ Get the children to include in the snapshot.

        This method is called to retrieve the children to include with
        the snapshot of the component. The default implementation just
        returns the list of `children`. Subclasses should reimplement
        this method if they need more control.

        Returns
        -------
        result : iterable
            An iterable of children to include in the component
            snapshot.

        """
        return self.children

    def traverse(self, depth_first=False):
        """ Yields all of the nodes in the tree, from this node downward.

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
            stack_extend(item.children)
    
    def traverse_ancestors(self, root=None):
        """ Yields all of the nodes in the tree, from the parent of this 
        node updward, stopping at the given root.

        Parameters
        ----------
        root : Declarative, optional
            The component at which to stop the traversal. Defaults
            to None

        """
        parent = self.parent
        while parent is not root and parent is not None:
            yield parent
            parent = parent.parent

    def find(self, name, regex=False):
        """ Locate and return the first named item that exists in the 
        subtree which starts at this node.

        This method will traverse the tree of components, breadth first,
        from this point downward, looking for a component with the given
        name. The first one with the given name is returned, or None if
        no component is found.

        Parameters
        ----------
        name : string
            The name of the component for which to search.
        
        regex : bool, optional
            Whether the given name is a regex string which should be
            matched against the names of children instead of tested
            for equality. Defaults to False.

        Returns
        -------
        result : Declarative or None
            The first component found with the given name, or None if 
            no component is found.
        
        """
        if regex:
            rgx = re.compile(name)
            match = lambda n: bool(rgx.match(n))
        else:
            match = lambda n: n == name
        for cmpnt in self.traverse():
            if match(cmpnt.name):
                return cmpnt

    def find_all(self, name, regex=False):
        """ Locate and return all the named items that exist in the
        subtree which starts at this node.

        This method will traverse the tree of components, breadth first,
        from this point downward, looking for a components with the given
        name.

        Parameters
        ----------
        name : string
            The name of the components for which to search.
        
        regex : bool, optional
            Whether the given name is a regex string which should be
            matched against the names of children instead of tested
            for equality. Defaults to False.

        Returns
        -------
        result : list of Declarative
            The list of components found with the given name, or an
            empty list if no components are found.
        
        """
        if regex:
            rgx = re.compile(name)
            match = lambda n: bool(rgx.match(n))
        else:
            match = lambda n: n == name
        res = []
        push = res.append
        for cmpnt in self.traverse():
            if match(cmpnt.name):
                push(cmpnt)
        return res
    
    def when(self, switch):
        """ A method which returns itself or None based on the truth of
        the argument.

        This can be useful to easily turn off the effects of a component
        if various situations such as constraints-based layout.

        Parameters
        ----------
        switch : bool
            A boolean which indicates whether the instance or None 
            should be returned.
        
        Returns
        -------
        result : self or None
            If 'switch' is boolean True, self is returned. Otherwise,
            None is returned.

        """
        if switch:
            return self

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    _trait_change_notify_flag = Bool(True)
    def trait_set(self, trait_change_notify=True, **traits):
        """ An overridden HasTraits method which keeps track of the
        trait change notify flag.

        The default implementation of trait_set has side effects if a
        call to setattr(...) causes a recurse into trait_set in that
        the notification context of the original call will be reset.

        This reimplemented method will make sure that context is reset
        appropriately for each call. This is required for Enaml since
        bound attributes are lazily computed and set quitely on the
        fly. 

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

