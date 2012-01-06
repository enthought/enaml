#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import deque

from traits.api import (
    Bool, HasStrictTraits, Instance, List, Property, Str, WeakRef,
    cached_property, Event, Dict, TraitType, Any, Disallow,
)

from ..expressions import AbstractExpression
from ..guard import guard
from ..styling.color import ColorTrait
from ..styling.font import FontTrait
from ..toolkit import Toolkit


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
        val = obj.expressions[name][-1].eval()
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


class FreezeContext(object):
    """ A context manager which disables rendering updates of a component
    on enter, and re-enables them on exit. It may safely nested.

    """
    _counts = {}

    @classmethod
    def is_frozen(cls, component):
        """ Returns a boolean indicating whether or not the given 
        component is currently the subject of a freeze context.

        """
        return component in cls._counts

    def __init__(self, component):
        """ Initialize a freeze context.

        Parameters
        ----------
        component : BaseComponent
            The component that should be frozen.
        
        """
        self.component = component
    
    def __enter__(self):
        """ Disables updates on the component the first time that any
        freeze context on that component is entered.

        """
        counts = self._counts
        cmpnt = self.component
        if cmpnt not in counts:
            counts[cmpnt] = 1
            cmpnt.disable_updates()
        else:
            counts[cmpnt] += 1
    
    def __exit__(self, exc_type, exc_value, traceback):
        """ Enables updates on the component when the last freeze
        context on that component is exited.

        """
        counts = self._counts
        cmpnt = self.component
        counts[cmpnt] -= 1
        if counts[cmpnt] == 0:
            del counts[cmpnt]
            cmpnt.enable_updates()


class AbstractTkBaseComponent(object):
    """ The abstract toolkit BaseComponent interface.

    A toolkit BaseComponent is responsible for creating and initializing
    the state of its implementation and binding event handlers.

    """
    __metaclass__ = ABCMeta
    
    @abstractproperty
    def toolkit_widget(self):
        """ An abstract property that should return the gui toolkit 
        widget being managed by the object.

        """
        raise NotImplementedError

    @abstractproperty
    def shell_obj(self):
        """ An abstract property that should *get* and *set* a reference
        to the shell object (an instance of BaseComponent). 

        It is suggested that the implementation maintain only a weakref
        to the shell object in order to avoid reference cycles. This 
        value will be set by the framework before any other creation or 
        initialization methods are called. It is performed in depth
        first order.

        """
        raise NotImplementedError

    @abstractmethod
    def create(self, parent):
        """ Create the underlying implementation object. 

        This method is called after the reference to the shell object
        has been set and is called in depth-first order. This means
        that by the time this method is called, the logical parent
        of this instance has already been created.

        Parameters
        ----------
        parent : toolkit widget or None
            The toolkit widget that will be the parent for the internal
            widget.

        """
        raise NotImplementedError
    
    @abstractmethod
    def initialize(self):
        """ Initialize the implementation object.

        This method is called after 'create' in depth-first order. This
        means that all other implementations in the tree will have been
        created so that intialization can depend on the existence of 
        other implementation objects.

        """
        raise NotImplementedError

    @abstractmethod
    def bind(self):
        """ Called after 'initialize' in order to bind event handlers.

        At the time this method is called, the entire tree of ui
        objects will have been initialized. The intention of this 
        method is delay the binding of event handlers until after
        everything has been intialized in order to mitigate extraneous
        event firing.

        """
        raise NotImplementedError

    @abstractmethod
    def destroy(self):
        """ Called when the underlying widget should be destroyed.

        This method is called before the child shell object is removed
        from its parent. This enables a toolkit backend to ensure that
        the underlying toolkit widget objects are properly removed 
        from the widget tree before the abstract wrapper is discarded.
                
        """
        raise NotImplementedError

    @abstractmethod
    def disable_updates(self):
        """ Called when the widget should disable its rendering updates.

        This is used before a large change occurs to a live ui so that
        the widget can optimize/delay redrawing until all the updates
        have been completed and 'enable_updates' is called.

        """
        raise NotImplementedError

    @abstractmethod
    def enable_updates(self):
        """ Called when the widget should enable rendering updates.

        This is used in conjunction with 'disable_updates' to allow
        a widget to optimize/delay redrawing until all the updates
        have been completed and this function is called.

        """
        raise NotImplementedError

    @abstractmethod
    def set_visible(self, visible):
        """ Set the visibility of the of the widget according to the
        given boolean.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_enabled_changed(self, enabled):
        """ The change handler for the 'enabled' attribute on the shell
        object. Sets the enabled/disabled state of the widget.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_bg_color_changed(self, color):
        """ The change handler for the 'bg_color' attribute on the shell
        object. Sets the background color of the internal widget to the 
        given color.
        
        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_fg_color_changed(self, color):
        """ The change handler for the 'fg_color' attribute on the shell
        object. Sets the foreground color of the internal widget to the 
        given color. For some widgets this may do nothing.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_font_changed(self, font):
        """ The change handler for the 'font' attribute on the shell
        object. Sets the font of the internal widget to the given font.
        For some widgets this may do nothing.

        """
        raise NotImplementedError


class BaseComponent(HasStrictTraits):
    """ The most base class of the Enaml component heierarchy.

    All Enaml classes should inherit from this class. This class is not 
    meant to be used directly.

    """
    #: The parent component of this component. It is stored as a weakref
    #: to mitigate issues with reference cycles. A top-level component's
    #: parent is None.
    parent = WeakRef('BaseComponent')

    #: The list of child for this component. This is read-only cached
    #: property that is computed based on the list of static children
    #: and the children contributed from any Include nodes. This list
    #: should not be directly manipulated
    children = Property(List, depends_on='_subcomponents:_components_updated')

    #: The dictionary of expression objects that are bound to attributes
    #: on this component. This should not normally be manipulated directly
    #: by the user. The bind_attribute method should be used instead if 
    #: proper default value initialization is desired.
    expressions = Dict(Str, List(Instance(AbstractExpression)))

    #: The list of include nodes for this component.
    #: The toolkit specific object that implements the behavior of
    #: this component and manages the gui toolkit object. Subclasses
    #: should redefine this trait to specify the specialized type of
    #: abstract_obj that is accepted.
    abstract_obj = Instance(AbstractTkBaseComponent) 

    #: A read-only property that returns the toolkit specific widget
    #: being managed by the abstract widget.
    toolkit_widget = Property

    #: Whether the component has been initialized or not. This will be 
    #: set to True after all of the setup() steps defined here are 
    #: completed. It should not be changed afterwards. This can be used 
    #: to trigger certain actions that need to occur after the component 
    #: has been set up.
    initialized = Bool(False)

    #: An optional name to give to this component to assist in finding
    #: it in the tree.
    name = Str

    #: A reference to the toolkit that created this object. This does 
    #: not need to be stored weakly because the toolkit does not maintain
    #: refs to the compoents that its constructors create.
    toolkit = Instance(Toolkit)
    
    #: The background color of the widget
    bg_color = ColorTrait
    
    #: The foreground color of the widget
    fg_color = ColorTrait
    
    #: The foreground color of the widget
    font = FontTrait

    #: Whether or not the widget is enabled.
    enabled = Bool(True)

    #: Whether or not the widget is visible.
    visible = Bool(True)

    #: A property which returns whether or not this component is 
    #: currently frozen.
    frozen = Property

    #: The private internal list of sub components for this component. 
    #: This list should not be manipulated by the user, and should not 
    #: be changed after initialization. It can, however, be redefined
    #: by subclasses to limit the type or number of subcomponents.
    _subcomponents = List(Instance('BaseComponent'))

    #: A private event that should be emitted by a component when the 
    #: results of calling _get_compenents() will result in new values. 
    #: This event is listened to by the parent of subcomponents in order 
    #: to know when to rebuild its list of children. User code will not 
    #: typically interact with this event.
    _components_updated = Event

    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_children(self):
        """ The cached property getter for the 'children' attribute.

        This property getter returns the flattened list of components
        returned by calling 'get_components()' on each subcomponent.

        """
        return sum([c.get_components() for c in self._subcomponents], [])

    def _get_toolkit_widget(self):
        """ The property getter for the 'toolkit_widget' attribute.

        """
        return self.abstract_obj.toolkit_widget

    def _get_frozen(self):
        """ The property getter for the 'frozen' attribute.

        """
        return FreezeContext.is_frozen(self)

    #--------------------------------------------------------------------------
    # Component Manipulation
    #--------------------------------------------------------------------------
    def get_components(self):
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
        self._subcomponents.append(component)
        
    #--------------------------------------------------------------------------
    # Attribute Binding 
    #--------------------------------------------------------------------------
    def bind_expression(self, name, expression):
        """ Binds the given expression to the attribute 'name'. If
        the attribute does not exist, one is created.

        If the object is not yet initialized, the expression will be 
        evaulated as the default value of the attribute on-demand.
        If the object is already initialized, then the expression
        is evaluated and the attribute set with the value. A strong
        reference to the expression object is kept internally. Mutliple
        expressions may be bound to the same attribute, but only the
        most recently bound expression will be used to compute the
        default value.
        
        Parameters
        ----------
        name : string
            The name of the attribute on which to bind the expression.
        
        expression : AbstractExpression
            An implementation of enaml.expressions.AbstractExpression.
        
        """
        expressions = self.expressions
        if name not in expressions:
            expressions[name] = []
        expressions[name].append(expression)
        
        if not self.initialized:
            curr = self.trait(name)
            if curr is None or curr is Disallow:
                # If no trait exists, then the user is requesting to add 
                # an attribute to the object. The HasStrictTraits may 
                # give a Disallow trait for attributes that don't exist.
                self.add_trait(name, Any())
                curr = self.trait(name)

            # We only need to add an ExpressionTrait once since it 
            # will reach back into the _expressions dict when needed
            # and retrieve the most current expression.
            if not isinstance(curr.trait_type, ExpressionTrait):
                self.add_trait(name, ExpressionTrait(curr))
        else:
            setattr(self, name, expression.eval())

    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def setup(self, parent=None):
        """ Run the setup process for the ui tree.

        The setup process is fairly complex and involves multiple steps.
        The complexity is required in order to ensure a consistent state
        of the object tree so that default values that are computed from
        expressions have the necessary information available.

        The setup process is comprised of the following steps:
        
        1) Child shell objects are given a reference to their parent
        2) Abstract objects create their internal toolkit object
        3) Abstract objects initialize their internal toolkit object
        4) Bount expression values are explicitly applied.
        5) Abstract objects bind their event handlers
        6) Abstract objects are added as a listeners to the shell object
        7) Visibility is initialized (toplevel nodes are skipped)
        8) Layout is initialized
        9) Nodes are marked as initialized

        Each of the setup steps is performed in depth-first order. This 
        method should only be called on the root node of the tree.

        Parameters
        ----------
        parent : native toolkit widget, optional
            If embedding this BaseComponent into a non-Enaml GUI, use 
            this to pass the appropriate toolkit widget that should be 
            the parent toolkit widget for this component.

        """
        self._setup_parent_refs()
        self._setup_create_widgets(parent)
        self._setup_init_widgets()
        self._setup_eval_expressions()
        self._setup_bind_widgets()
        self._setup_listeners()
        self._setup_init_visibility()
        self._setup_init_layout()
        self._setup_set_initialized()

    def _setup_parent_refs(self):
        """ A setup method which assigns the parent reference to the
        static children.

        """
        for child in self._subcomponents:
            child.parent = self
            child._setup_parent_refs()

    def _setup_create_widgets(self, parent):
        """ A setup method that tells the abstract object to create its
        internal toolkit object.

        """
        self.abstract_obj.create(parent)
        self_widget = self.toolkit_widget
        for child in self._subcomponents:
            child._setup_create_widgets(self_widget)

    def _setup_init_widgets(self):
        """ A setup method that tells the abstract object to initialize
        its internal toolkit object.

        """
        self.abstract_obj.initialize()
        for child in self._subcomponents:
            child._setup_init_widgets()

    def _setup_eval_expressions(self):
        """ A setup method that loops over all of bound expressions and
        performs a getattr for those attributes. This ensures that all
        bound attributes are initialized, since it won't alway be the
        case that the previous initialization step will pull all of the
        values, but they nevertheless need to be applied.

        """
        for name in self.expressions:
            getattr(self, name)
        for child in self._subcomponents:
            child._setup_eval_expressions()

    def _setup_bind_widgets(self):
        """ A setup method that tells the abstract object to bind its
        event handlers to its internal toolkit object.

        """
        self.abstract_obj.bind()
        for child in self._subcomponents:
            child._setup_bind_widgets()

    def _setup_listeners(self):
        """ A setup method which sets the abstract object as a traits 
        listener for this component with a prefix of 'shell'.

        """
        self.add_trait_listener(self.abstract_obj, 'shell')
        for child in self._subcomponents:
            child._setup_listeners()

    def _setup_init_visibility(self):
        """ A setup method called to initialize the visibility. This
        is called before the components are marked as initialized, so
        it will not have an effect on toplevel nodes or cause any 
        layout to take place.

        """
        self.set_visible(self.visible)
        for child in self._subcomponents:
            child._setup_init_visibility()

    def _setup_init_layout(self):
        """ A setup method called at the end of the setup process, but 
        before the 'initialized' attribute it set to True. This setup
        method is performed bottom-up so that children have a chance
        to compute their sizes before reporting them to their parent.

        """
        for child in self._subcomponents:
            child._setup_init_layout()
        self.initialize_layout()

    def _setup_set_initialized(self):
        """ A setup method whic ets the initialized attribute to True.

        """
        self.initialized = True
        for child in self._subcomponents:
            child._setup_set_initialized()

    #--------------------------------------------------------------------------
    # Teardown Methods
    #--------------------------------------------------------------------------
    def destroy(self):
        """ Destroys the underlying toolkit widget as well as all of
        the children of this component. After calling this method, the
        component and all of its children should be considered invalid
        and no longer used.

        """
        # Remove the abstract object as a trait listener so that it
        # does not try to update after destroying its internal widget.
        self.remove_trait_listener(self.abstract_obj, 'shell')
        self.abstract_obj.destroy()
        for child in self._subcomponents:
            child.destroy()
        self.abstract_obj = None
        self._subcomponents = []

    #--------------------------------------------------------------------------
    # Layout Stubs 
    #--------------------------------------------------------------------------
    def initialize_layout(self):
        """ A method called during the setup process to initialize layout. 
        By default, it does nothing. Subclasses should reimplement this
        method as required.

        """
        pass

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

    def relayout_later(self):
        """ A method called when the layout of the component's children
        should be refreshed at some point in the future. By default, this 
        method proxies the call up the hierarchy until an implementor is 
        found. Any implementors should ensure that this method returns 
        immediately, and that relayout occurs at some point in the future.

        """
        parent = self.parent
        if parent is not None:
            parent.relayout_later()

    def rearrange(self):
        """ A method called when the positioning of the component's 
        children should be refreshed. By default, this method proxies the 
        call up the hierarchy until an implementor is found. Implementors 
        should ensure that this method takes place immediately, and that
        the refresh is complete before the method returns. 

        Note: This method performs less work than 'relayout' and should 
            typically only need to be called when the children need to 
            be repositioned, rather than have all of their layout 
            relationships recomputed.

        """
        parent = self.parent
        if parent is not None:
            parent.rearrange()
        
    def rearrange_later(self):
        """ A method called when the positioning of the component's 
        children should be refreshed at some point in the future. By 
        default, this method proxies the call up the hierarchy until an 
        implementor is found. Implementors should ensure that this method 
        returns immediately, and that the refresh is completed at some 
        time in the future.
        
        Note: This method performs less work than 'relayout' and should 
            typically only need to be called when the children need to 
            be repositioned, rather than have all of their layout 
            relationships recomputed.

        """
        parent = self.parent
        if parent is not None:
            parent.rearrange_later()
        
    def relayout_enqueue(self, callable):
        """ Enqueue a callable to be executed in a frozen context on the
        next relayout pass. By default, this method proxies the call up
        the hierarchy until an implementor is found. Implementors should
        ensure that enqueuing the callable results in a relayout later
        which empties the queue from within a freeze context.

        """
        parent = self.parent
        if parent is not None:
            parent.relayout_enqueue(callable)
        
    def rearrange_enqueue(self, callable):
        """ Enqueue a callable to be executed in a frozen context on the
        next rearrange pass. By default, this method proxies the call up
        the hierarchy until an implementor is found. Implementors should
        ensure that enqueuing the callable results in a rearrange later
        which empties the queue from within a freeze context.

        """
        parent = self.parent
        if parent is not None:
            parent.rearrange_enqueue(callable)
    
    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def _children_changed(self):
        """ Handles the children being changed on this component by 
        enqueing a relayout provided that the component is initialized.

        """
        if self.initialized:
            # We only need to make sure things get a relayout. We can 
            # do this by simply enqueuing an empty callable. This makes
            # sure we don't trigger multiple relayouts if some other
            # part of the framework has requested the same.
            self.relayout_enqueue(lambda: None)

    def _visible_changed(self, visible):
        """ Handles the 'visible' attribute being changed by calling the
        'set_visible' method.

        """
        # The method call allows the visibility to be set by other parts 
        # of the framework which are not dependent on change notification.
        # By using the method here, we help to ensure a consistent state.
        self.set_visible(visible)

    #--------------------------------------------------------------------------
    # Auxiliary Methods 
    #--------------------------------------------------------------------------
    def set_visible(self, visible):
        """ Set the visibility of the component according to the given
        boolean. There is protection logic in place to ensure a that 
        the visibility state remains consistent throughout the lifetime 
        of the component.

        """
        # Make sure the 'visible' attribute is synced up as a result
        # of the method call. This may fire a notification, in which
        # case the change handler will call this method again. This
        # guard prevents that unneeded recursion.
        if guard.guarded(self, 'set_visible'):
            return
        else:
            with guard(self, 'set_visible'):
                self.visible = visible

        if self.initialized:
            if self.parent is None:
                # If the component is initialized and it is a toplevel
                # component, then it is safe to set the visibility
                # immediately. 
                #
                # XXX we need to pump the event loop a couple of times 
                # to get things to initialize properly. It would be good
                # to not have to do this.
                self.toolkit.process_events()
                self.toolkit.process_events()
                self.abstract_obj.set_visible(visible)
            else:
                # If the component is initialized but it is not toplevel,
                # then the visibility change must occur in a deferred
                # context, since changing the visibility of a nested
                # component will require a layout update.
                def visibility_closure():
                    self.abstract_obj.set_visible(visible)
                self.relayout_enqueue(visibility_closure)
        else:
            # If the component is not yet initialized, and it is not a 
            # toplevel component, then it is safe to set the visibility
            # immediately since a visible child of a non-visible parent 
            # will remain hidden until its parent is shown. For toplevel
            # components which are uninitialized, this method is a no-op 
            # since it would not yet be safe to display the widget.
            if self.parent is not None:
                self.abstract_obj.set_visible(visible)

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

    def disable_updates(self):
        """ Disables rendering updates for the underlying widget.

        """
        self.abstract_obj.disable_updates()

    def enable_updates(self):
        """ Enables rendering updates for the underlying widget.

        """
        self.abstract_obj.enable_updates()

    def freeze(self):
        """ A context manager which disables rendering updates on 
        enter and restores them on exit. The context can be safetly
        nested and updates will be applied and the component will be
        relayed out when the top-most context is exited.

        """
        return FreezeContext(self)

