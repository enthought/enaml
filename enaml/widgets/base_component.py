#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import deque

from traits.api import (
    Bool, HasStrictTraits, Instance, List, Property, Str, WeakRef,
    cached_property, Dict, TraitType, Disallow,
)

from ..expressions import AbstractExpression
from ..toolkit import Toolkit
from ..util.trait_types import EnamlInstance, EnamlEvent


#------------------------------------------------------------------------------
# Expression Trait
#------------------------------------------------------------------------------
class ExpressionTrait(TraitType):
    """ A custom trait type which is used to help implement expression 
    binding.

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

    def get(self, obj, name):
        """ Handle the computing the initial value for the expression
        trait. This method first restores the old trait, then evaluates
        the expression and sets the value on the trait. It then performs
        a getattr to return the new value of the trait. If the object
        is not yet fully initialized, the value is set quietly.

        """
        self.swapout(obj, name)
        val = obj._expressions[name].eval()
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
# UserAttribute
#------------------------------------------------------------------------------
class UninitializedAttributeError(Exception):
    """ A custom Exception used by UserAttribute to signal the access 
    of an uninitialized attribute.

    """
    # XXX - We can't inherit from AttributeError because the local 
    # scope object used by expressions captures an AttributeError
    # and converts it into in a KeyError in order to implement
    # dynamic attribute scoping. 
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
        notification will carry the traits Undefined object as the old
        value.

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

    def full_info(self, obj, name, value):
        """ Overridden parent class method to compute an appropriate info
        string for use in error messages.

        """
        return 'an instance of %s' % self.base_type


#------------------------------------------------------------------------------
# User Event
#------------------------------------------------------------------------------
class UserEvent(EnamlEvent):
    """ A simple EnamlEvent subclass used to distinguish between events
    declared by the framework, and events declared by the user.

    """
    pass


#------------------------------------------------------------------------------
# Enaml Base Component
#------------------------------------------------------------------------------
class BaseComponent(HasStrictTraits):
    """ The most base class of the Enaml component heierarchy.

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
    #: user. Rather, expressions should be added by calling the 
    #: 'bind_expression' method.
    _expressions = Dict(Str, Instance(AbstractExpression))

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
        """ Returns the list of BaseComponent instance which should be
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
    # Attribute Manipulation
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
            
        # At this point we know there are non non-overridable traits 
        # defined for the object, but it is possible that there are 
        # methods or other non-trait attributes using the given name. 
        # We could  potentially check for those, but its probably more 
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

    def bind_expression(self, name, expression):
        """ Binds the given expression to the attribute 'name'. If
        the attribute does not exist, one is created.

        If the object is not yet initialized, the expression will be 
        evaulated as the default value of the attribute on-demand.
        If the object is already initialized, then the expression
        is evaluated immediately and the attribute set with the value. 
        A strong reference to the expression object is kept internally.
        
        Parameters
        ----------
        name : string
            The name of the attribute on which to bind the expression.
        
        expression : AbstractExpression
            An implementation of enaml.expressions.AbstractExpression.
        
        """
        # In the below clauses of the if-block, the line of code which
        # assigns into the _expressions dict is repeated on purpose, 
        # instead of being pulled out to this level. This is because the
        # _expressions dict needs to be updated before we add an 
        # ExpressionTrait or perform a setattr but *not* if the inner 
        # if-clause of the if-block raises an exception.
        if not self.initialized:
            curr = self.trait(name)
            if curr is None or curr.trait_type is Disallow:
                msg = "Cannot bind expression. %s object has no attribute '%s'"
                raise AttributeError(msg % (self, name))
        
            # This explicitly overrides any existing bound expression 
            # for the given attribute, which means that the most 
            # recently bound expression takes precedence.
            self._expressions[name] = expression

            # We only need to add an ExpressionTrait once since it 
            # will reach back into the _expressions dict when needed
            # and retrieve the bound expression.
            if not isinstance(curr.trait_type, ExpressionTrait):
                self.add_trait(name, ExpressionTrait(curr))
        else:
            # This explicitly overrides any existing bound expression 
            # for the given attribute, which means that the most 
            # recently bound expression takes precedence.
            self._expressions[name] = expression
            setattr(self, name, expression.eval())

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
        
        1) Abstract objects create their internal toolkit object
        2) Abstract objects initialize their internal toolkit object
        3) Bound expression values are explicitly applied
        4) Abstract objects bind their event handlers
        5) Abstract objects are added as a listeners to the shell object
        6) Visibility is initialized
        7) Layout is initialized
        8) A finalization pass is made
        9) Nodes are marked as initialized

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
        the component to True.

        """
        self.initialized = True
        for child in self._subcomponents:
            child._setup_set_initialized()

    #--------------------------------------------------------------------------
    # Teardown Methods
    #--------------------------------------------------------------------------
    def destroy(self):
        """ Destroys the component by clearing the list of subcomponents
        and calling 'destroy' on all of the old subcomponents. Subclasses
        that need more control over destruction should reimplement this
        method.

        """
        for child in self._subcomponents:
            child.destroy()
        self._subcomponents = []

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

