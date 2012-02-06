#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import deque

from traits.api import (
    Bool, HasStrictTraits, Instance, List, Property, Str, WeakRef,
    cached_property, Dict, TraitType, Disallow,
)

from .expressions import AbstractExpression
from .toolkit import Toolkit
from .trait_types import EnamlInstance, EnamlEvent


#------------------------------------------------------------------------------
# Expression Trait
#------------------------------------------------------------------------------
class ExpressionTrait(TraitType):
    """ A custom trait type which is used to help implement expression 
    binding. Instances of this trait are added to an object, but swap
    themselves out and replace the old trait the first time they are
    accessed. This allows bound expressions to be initialized in the
    proper order without requiring an explicit initialization graph.

    """
    def __init__(self, old_trait):
        """ Initialize an expression trait.

        Parameters
        ----------
        old_trait : ctrait
            The trait object that the expression trait is temporarily
            replacing. When a 'get' or 'set' is triggered on this 
            trait, the old trait will be restored and then the default
            value of the expression will be applied.
        
        """
        super(ExpressionTrait, self).__init__()
        self.old_trait = old_trait
    
    def swapout(self, obj, name):
        """ Restore the old trait onto the object. This method takes
        care to make sure that listeners are copied over properly.

        """
        # The default behavior of add_trait does *almost* the right
        # thing when it copies over notifiers when replacing the
        # existing trait. What it fails to do is update the owner
        # attribute of TraitChangeNotifyWrappers which are managing
        # a bound method notifier. This means that if said notifier
        # ever dies, it removes itself from the incorrect owner list
        # and it will be (erroneously) called on the next dispatch
        # cycle. The logic here makes sure that the owner attribute
        # of such a notifier is properly updated with its new owner.
        obj.add_trait(name, self.old_trait)
        notifiers = obj.trait(name)._notifiers(0)
        if notifiers is not None:
            for notifier in notifiers:
                if hasattr(notifier, 'owner'):
                    notifier.owner = notifiers

    def compute_default(self, obj, name):
        """ Returns the default value as computed by the most recently
        bound expression. If a value cannot be provided, NotImplemented
        is returned.

        """
        res = NotImplemented
        expr = obj._expressions[name][0]
        if expr is not None:
            res = expr.eval()
        return res

    def get(self, obj, name):
        """ Handle computing the initial value for the expression trait. 
        This method first restores the old trait, then evaluates the 
        expression and sets the value on the trait. It then performs
        a getattr to return the new value of the trait. If the object
        is not yet fully initialized, the value is set quietly.

        """
        self.swapout(obj, name)
        val = self.compute_default(obj, name)
        if val is not NotImplemented:
            if not obj.initialized:
                obj.trait_setq(**{name: val})
            else:    
                setattr(obj, name, val)
        return getattr(obj, name, val)

    def set(self, obj, name, val):
        """ Handle the setting of an initial value for the expression
        trait. This method first restores the old trait, then sets
        the value on that trait. In this case, the expression object
        is not needed. If the object is not yet fully initialized, the 
        value is set quietly.

        """
        self.swapout(obj, name)
        if not obj.initialized:
            obj.trait_setq(**{name: val})
        else:
            setattr(obj, name, val)


#------------------------------------------------------------------------------
# User Attribute and Event
#------------------------------------------------------------------------------
class UninitializedAttributeError(Exception):
    """ A custom Exception used by UserAttribute to signal the access 
    of an uninitialized attribute.

    """
    # XXX - We can't inherit from AttributeError because the local 
    # scope object used by expressions captures an AttributeError
    # and converts it into in a KeyError in order to implement
    # dynamic attribute scoping. We actually want this exception
    # to propagate.
    pass


class UserAttribute(EnamlInstance):
    """ An EnamlInstance subclass that is used to implement optional 
    attribute typing when adding a new user attribute to an Enaml 
    component.

    """
    def get(self, obj, name):
        """ The trait getter method. Returns the value from the object's
        dict, or raises an uninitialized error if the value doesn't exist.

        """
        dct = obj.__dict__
        if name not in dct:
            self.uninitialized_error(obj, name)
        return dct[name]

    def set(self, obj, name, value):
        """ The trait setter method. Sets the value in the object's 
        dict if it is valid, and emits a change notification if the
        value has changed. The first time the value is set the change
        notification will carry None as the old value.

        """
        value = self.validate(obj, name, value)
        dct = obj.__dict__
        if name not in dct:
            old = None
        else:
            old = dct[name]
        dct[name] = value
        if old != value:
            obj.trait_property_changed(name, old, value)

    def uninitialized_error(self, obj, name):
        """ A method which raises an UninitializedAttributeError for
        the given object and attribute name

        """
        msg = "Cannot access the uninitialized '%s' attribute of the %s object"
        raise UninitializedAttributeError(msg % (name, obj))


class UserEvent(EnamlEvent):
    """ A simple EnamlEvent subclass used to distinguish between events
    declared by the framework, and events declared by the user.

    """
    pass


#------------------------------------------------------------------------------
# Enaml Base Component
#------------------------------------------------------------------------------
class BaseComponent(HasStrictTraits):
    """ The most base class of the Enaml component hierarchy.

    All declarative Enaml classes should inherit from this class. This 
    class is not meant to be instantiated directly.

    """
    #: A readonly property which returns the current instance of
    #: the component. This allows declarative Enaml components to
    #: access self according to the standard attribute scoping rules.
    self = Property

    #: The parent component of this component. It is stored as a weakref
    #: to mitigate issues with reference cycles. A top-level component's
    #: parent is None.
    parent = WeakRef('BaseComponent')

    #: The list of children for this component. This is a read-only
    #: cached property that is computed based on the static list of
    #: _subcomponents and the items they return by calling their
    #: 'get_actual' method. This list should not be manipulated by
    #: user code.
    children = Property(List(Instance('BaseComponent')), 
                        depends_on='_subcomponents:_actual_updated')

    #: Whether the component has been initialized or not. This will be 
    #: set to True after all of the setup() steps defined here are 
    #: completed. It should not be changed afterwards. This can be used 
    #: to trigger certain actions that need to occur after the component 
    #: has been set up.
    initialized = Bool(False)

    #: An optional name to give to this component to assist in finding
    #: it in the tree. See the 'find_by_name' method.
    name = Str

    #: A reference to the toolkit that was used to create this object.
    toolkit = Instance(Toolkit)

    #: The private dictionary of expression objects that are bound to 
    #: attributes on this component. It should not be manipulated by
    #: user code. Rather, expressions should be bound by calling the 
    #: 'bind_expression' method.
    _expressions = Dict(Str, List(Instance(AbstractExpression)))

    #: The private list of virtual base classes that were used to 
    #: instantiate this component from Enaml source code. The 
    #: EnamlFactory class of the Enaml runtime will directly append
    #: to this list as necessary.
    _bases = List

    #: The private internal list of subcomponents for this component. 
    #: This list should not be manipulated by the user, and should not
    #: be changed after initialization. It can, however, be redefined
    #: by subclasses to limit the type or number of subcomponents.
    _subcomponents = List(Instance('BaseComponent'))

    #: A private event that should be emitted by a component when the 
    #: results of calling get_actual() will result in new values. 
    #: This event is listened to by the parent of subcomponents in order 
    #: to know when to rebuild its list of children. User code will not 
    #: typically interact with this event.
    _actual_updated = EnamlEvent

    #: The HasTraits class defines a class attribute 'set' which is
    #: a deprecated alias for the 'trait_set' method. The problem
    #: is that having that as an attribute interferes with the 
    #: ability of Enaml expressions to resolve the builtin 'set',
    #: since the dynamic attribute scoping takes precedence over
    #: builtins. This resets those ill-effects.
    set = Disallow

    #--------------------------------------------------------------------------
    # Special Methods
    #--------------------------------------------------------------------------
    def __repr__(self):
        """ An overridden repr which returns the repr of the factory 
        from which this component is derived, provided that it is not 
        simply a root constructor. Otherwise, it defaults to the super
        class' repr implementation.

        """
        # If there are any bases, the last one in the list will always 
        # be a constructor. We want to ignore that one and focus on the
        # repr of the virtual base class from which the component was 
        # derived in the Enaml source code.
        bases = self._bases
        if len(bases) >= 2:
            base = bases[0]
            return repr(base)
        return super(BaseComponent, self).__repr__()

    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    def _get_self(self):
        """ The property getter for the 'self' attribute.

        """
        return self
        
    @cached_property
    def _get_children(self):
        """ The cached property getter for the 'children' attribute.

        This property getter returns the flattened list of components
        returned by calling 'get_actual()' on each subcomponent.

        """
        return sum([c.get_actual() for c in self._subcomponents], [])

    #--------------------------------------------------------------------------
    # Component Manipulation
    #--------------------------------------------------------------------------
    def get_actual(self):
        """ Returns the list of BaseComponent instances which should be
        included as proper children of our parent. By default this 
        simply returns [self]. This method should be reimplemented by 
        subclasses which need to contribute different components to their
        parent's children.

        """
        return [self]
        
    def add_subcomponent(self, component):
        """ Adds the given component as a subcomponent of this object.
        By default, the subcomponent is added to an internal list of 
        subcomponents. This method may be overridden by subclasses to 
        filter or otherwise handle certain subcomponents differently.

        """
        component.parent = self
        self._subcomponents.append(component)
    
    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def setup(self, parent=None):
        """ Run the setup process for the ui tree.

        The setup process is fairly complex and involves multiple steps.
        The complexity is required in order to ensure a consistent state
        of the component tree so that default values that are computed 
        from expressions have the necessary information available.

        The setup process is comprised of the following steps:
        
        1)  Abstract objects create their internal toolkit object
        2)  Abstract objects initialize their internal toolkit object
        3)  Bound expression values are explicitly applied
        4)  Abstract objects bind their event handlers
        5)  Abstract objects are added as listeners to the shell object
        6)  Visibility is initialized
        7)  Layout is initialized
        8)  A finalization pass is made
        9)  Nodes are marked as initialized
        
        Many of these setup methods are no-ops, but are defined on this
        BaseComponent for simplicity and continuity. Subclasses that
        need to partake in certain portions of the layout process 
        should re-implement the appropriate setup methods.

        Parameters
        ----------
        parent : native toolkit widget, optional
            If embedding this BaseComponent into a non-Enaml GUI, use 
            this to pass the appropriate toolkit widget that should be 
            the parent toolkit widget for this component.

        """
        self._setup_create_widgets(parent)
        self._setup_init_widgets()
        self._setup_eval_expressions()
        self._setup_bind_widgets()
        self._setup_listeners()
        self._setup_init_visibility()
        self._setup_init_layout()
        self._setup_finalize()
        self._setup_set_initialized()

    def _setup_create_widgets(self, parent):
        """ A setup method that, by default, is a no-op. Subclasses 
        that drive gui toolkit widgets should reimplement this method
        to create the underlying toolkit widget(s).

        """
        for child in self._subcomponents:
            child._setup_create_widgets(parent)

    def _setup_init_widgets(self):
        """ A setup method that, by default, is a no-op. Subclasses 
        that drive gui toolkit widgets should reimplement this method
        to initialize their internal toolkit widget(s).

        """
        for child in self._subcomponents:
            child._setup_init_widgets()

    def _setup_eval_expressions(self):
        """ A setup method that loops over all of bound expressions and
        performs a getattr for those attributes. This ensures that all
        bound attributes are initialized, even if they weren't implicitly
        initialized in any of the previous setup methods.

        """
        for name in self._expressions:
            getattr(self, name)
        for child in self._subcomponents:
            child._setup_eval_expressions()

    def _setup_bind_widgets(self):
        """ A setup method that, by default, is a no-op. Subclasses 
        that drive gui toolkit widgets should reimplement this method
        to bind any event handlers of their internal toolkit widget(s).

        """
        for child in self._subcomponents:
            child._setup_bind_widgets()

    def _setup_listeners(self):
        """ A setup method that, by default, is a no-op. Subclasses 
        that drive gui toolkit widgets should reimplement this method
        to setup an traits listeners necessary to drive their internal
        toolkit widget(s).

        """
        for child in self._subcomponents:
            child._setup_listeners()

    def _setup_init_visibility(self):
        """ A setup method that, by default, is a no-op. Subclasses 
        that drive gui toolkit widgets should reimplement this method
        to initialize the visibility of their widgets.

        """
        for child in self._subcomponents:
            child._setup_init_visibility()

    def _setup_init_layout(self):
        """ A setup method that, by default, is a no-op. Subclasses 
        that manage layout should reimplement this method to initialize
        their underlying layout.

        """
        for child in self._subcomponents:
            child._setup_init_layout()

    def _setup_finalize(self):
        """ A setup method that, by default, is a no-op. Subclasses
        that need to perform process after layout is initialized but
        before a node is marked as fully initialized should reimplement
        this method.

        """
        for child in self._subcomponents:
            child._setup_finalize()

    def _setup_set_initialized(self):
        """ A setup method which updates the initialized attribute of 
        the component to True. This is performed bottom-up.

        """
        for child in self._subcomponents:
            child._setup_set_initialized()
        self.initialized = True

    #--------------------------------------------------------------------------
    # Teardown Methods
    #--------------------------------------------------------------------------
    def destroy(self):
        """ Destroys the component by clearing the list of subcomponents
        and calling 'destroy' on all of the old subcomponents, then gets
        rid of all references to the subcomponents and bound expressions.
        Subclasses that need more control over destruction should 
        reimplement this method.

        """
        for child in self._subcomponents:
            child.destroy()
        del self._subcomponents[:]
        self._expressions.clear()

    #--------------------------------------------------------------------------
    # Layout Stubs
    #--------------------------------------------------------------------------
    def relayout(self):
        """ A method called when the layout of the component's children
        should be refreshed. By default, this method proxies the call up
        the hierarchy until an implementor is found. Any implementors 
        should ensure that the necessary operations take place immediately 
        and are complete before the method returns.

        """
        parent = self.parent
        if parent is not None:
            parent.relayout()

    def request_relayout(self):
        """ A method called when the layout of the component's children
        should be refreshed at some point in the future. By default, this 
        method proxies the call up the hierarchy until an implementor is 
        found. Any implementors should ensure that this method returns 
        immediately, and that relayout occurs at some point in the future.

        """
        parent = self.parent
        if parent is not None:
            parent.request_relayout()

    def refresh(self):
        """ A method called when the positioning of the component's 
        children should be refreshed. By default, this method proxies the 
        call up the hierarchy until an implementor is found. Implementors 
        should ensure that this method takes place immediately, and that
        the refresh is complete before the method returns. 

        Note: This method should perform less work than 'relayout' and 
            should typically only need to be called when the children 
            need to be repositioned, rather than have all of their layout 
            relationships recomputed.

        """
        parent = self.parent
        if parent is not None:
            parent.refresh()
        
    def request_refresh(self):
        """ A method called when the positioning of the component's 
        children should be refreshed at some point in the future. By 
        default, this method proxies the call up the hierarchy until an 
        implementor is found. Implementors should ensure that this method 
        returns immediately, and that the refresh is completed at some 
        time in the future.
        
        Note: This method should perform less work than 'relayout' and 
            should typically only need to be called when the children 
            need to be repositioned, rather than have all of their layout 
            relationships recomputed.

        """
        parent = self.parent
        if parent is not None:
            parent.request_refresh()
        
    def request_relayout_task(self, callback, *args, **kwargs):
        """ Schedule a callback to be executed, followed by a relayout. 
        By default, this method proxies the call up the hierarchy until 
        an implementor is found. Implementors should ensure that the
        callback is executed with given arguments at some point in the
        future and is followed by a relayout. It is suggested that 
        implementors collapse multiple calls to this method which
        results in a single relayout.

        """
        parent = self.parent
        if parent is not None:
            parent.request_relayout_task(callback, *args, **kwargs)
        
    def request_refresh_task(self, callback, *args, **kwargs):
        """ Schedule a callback to be executed, followed by a rerfresh. 
        By default, this method proxies the call up the hierarchy until 
        an implementor is found. Implementors should ensure that the
        callback is executed with given arguments at some point in the
        future and is followed by a relayout. It is suggested that 
        implementors collapse multiple calls to this method which
        results in a single refresh.

        """
        parent = self.parent
        if parent is not None:
            parent.request_refresh_task(callback, *args, **kwargs)

    #--------------------------------------------------------------------------
    # Bound Attribute Handling
    #--------------------------------------------------------------------------
    def add_attribute(self, name, attr_type=object, is_event=False):
        """ Adds an attribute to the base component with the given name
        and ensures that values assigned to this attribute are of a
        given type.

        If the object already has an attribute with the given name,
        an exception will be raised.

        Parameters
        ----------
        name : string
            The name of the attribute to add.
        
        attr_type : type-like object, optional
            An object that behaves like a type for the purposes of a
            call to isinstance. Defaults to object.
        
        is_event : bool, optional
            If True, the added attribute will behave like an event.
            Otherwise, it will behave like a normal attribute. The 
            default is False.

        """
        # Check to see if a trait is already defined. We don't use
        # hasattr here since that might prematurely trigger a trait
        # intialization. We allow overriding traits of type Disallow,
        # UserAttribute, and UserEvent. The first is a consequence of 
        # using HasStrictTraits, where non-existing attributes are 
        # manifested as a Disallow trait. The others allow a custom 
        # derived component to specialize the attribute and event types 
        # of the component from which it is deriving.
        curr = self.trait(name)
        if curr is not None:
            ttype = curr.trait_type
            allowed = (UserAttribute, UserEvent)
            if ttype is not Disallow and not isinstance(ttype, allowed):
                msg = ("Cannot add '%s' attribute. The '%s' attribute on "
                       "the %s object already exists.")
                raise TypeError(msg % (name, name, self))
            
        # At this point we know there are no non-overridable traits 
        # defined for the object, but it is possible that there are 
        # methods or other non-trait attributes using the given name. 
        # We could potentially check for those, but its probably more 
        # useful to allow for overriding such things from Enaml, so we 
        # just go ahead and add the attribute.
        try:
            if is_event:
                self.add_trait(name, UserEvent(attr_type))
            else:
                self.add_trait(name, UserAttribute(attr_type))
        except TypeError:
            msg = ("'%s' is not a valid type for the '%s' attribute "
                   "declaration on %s")
            raise TypeError(msg % (attr_type, name, self))

    def bind_expression(self, name, expression, notify_only=False):
        """ Binds the given expression to the attribute 'name'.
         
        If the attribute does not exist, an exception is raised. A 
        strong reference to the expression object is kept internally.
        If the expression is not notify_only and the object is already
        fully initialized, the value of the expression will be applied
        immediately.

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
        
            # Hookup support for default value computation.
            if not self.initialized:
                # We only need to add an ExpressionTrait once, since it 
                # will reach back into the _expressions dict as needed
                # and retrieve the bound expression.
                if not isinstance(curr.trait_type, ExpressionTrait):
                    self.add_trait(name, ExpressionTrait(curr))
            else:
                # If the component is already initialized, and the given
                # expression supports evaluation, update the attribute 
                # with the current value.
                val = expression.eval()
                if val is not NotImplemented:
                    setattr(self, name, val)

    def _on_expression_changed(self, expression, name, value):
        """ A private signal callback for the expression_changed signal
        of the bound expressions. It updates the value of the attribute
        with the new value from the expression.

        """
        setattr(self, name, value)
    
    def _on_bound_attr_changed(self, obj, name, old, new):
        """ A private handler which is called when any attribute which
        has a bound signal changes. It calls the notify method on each
        of the expressions bound to that attribute, but only after the
        component has been fully initialized.

        """
        # The check for None is for the case where there are no left 
        # associative expressions bound to the attribute, so the first
        # entry in the list is still None.
        if self.initialized:
            for expr in self._expressions[name]:
                if expr is not None:
                    expr.notify(old, new)

    #--------------------------------------------------------------------------
    # Auxiliary Methods 
    #--------------------------------------------------------------------------
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
        root : BaseComponent, optional
            The component at which to stop the traversal. Defaults
            to None

        """
        parent = self.parent
        while parent is not root and parent is not None:
            yield parent
            parent = parent.parent

    def find_by_name(self, name):
        """ Locate and return a named item that exists in the subtree
        which starts at this node.

        This method will traverse the tree of components, breadth first,
        from this point downward, looking for a component with the given
        name. The first one with the given name is returned, or None if
        no component is found.

        Parameters
        ----------
        name : string
            The name of the component for which to search.
        
        Returns
        -------
        result : BaseComponent or None
            The first component found with the given name, or None if 
            no component is found.
        
        """
        for cmpnt in self.traverse():
            if cmpnt.name == name:
                return cmpnt

    def toplevel_component(self):
        """ Walks up the tree of components starting at this node and
        returns the toplevel node, which is the first node encountered
        without a parent.

        """
        cmpnt = self
        while cmpnt is not None:
            res = cmpnt
            cmpnt = cmpnt.parent
        return res

