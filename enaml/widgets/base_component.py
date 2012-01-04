#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import deque

from traits.api import (
    Bool, HasStrictTraits, Instance, List, Property, Str, WeakRef,
    cached_property, Event, Dict, TraitType, Any
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
    def __init__(self, proxy_name):
        """ Initialize an expression trait.

        Parameters
        ----------
        proxy_name : string
            The attribute name to which this trait is proxying.
        
        init_quietly : bool
            Whether or not to silence trait listeners when initializing
            the trait attribute from the value of the expression.
        
        """
        super(ExpressionTrait, self).__init__()
        self.proxy_name = proxy_name
        self.inited = False

    def init_expr(self, obj, name):
        """ Initializes the value of the proxy trait using the value
        from the bound expression. Also hooks up the appropriate 
        notifiers so that changes to the proxy trait get forwarded
        as changes to this expression trait.

        """
        def notify(target_obj, target_name, old, new):
            """ Proxies an change event from the shadow trait to the
            target trait.

            """
            target_obj.trait_property_changed(name, old, new)
        
        def notify_items(target_obj, target_name, old, new):
            """ Proxies an items event from the shadow trait to the 
            target trait.

            """
            target_obj.trait_property_changed(name + '_items', old, new)

        # Traits magic numbers 5, 6, 9 correspond to List, Dict,
        # and Set, respectively. If we are proxying to one of those 
        # trait types, then we also need to listen to that items event.
        # Set the target of the notifier to self so that the notifier
        # gets destroyed when the object which contains this trait is
        # destroyed.
        proxy_name = self.proxy_name
        trait = obj.trait(proxy_name)
        obj.on_trait_change(notify, proxy_name, target=self)
        if trait.handler.default_value_type in (5, 6, 9):
            # For items events we need to bind two handlers. Traits gets
            # a bit weird when using the 'trait_name[]' style syntax to
            # bind a single handler to both the object and items events
            # and then trying to proxy that notification to another 
            # trait. However, using two separate handlers seems to be ok.
            items_name = proxy_name + '_items'
            obj.on_trait_change(notify_items, items_name, target=self)
        
        # Next, eval the expression and set the value of the proxy,
        # silencing notifiers if the object is not initialized since
        # attribute assigment before initialization should appear as
        # a default value assignment which does not fire notifiers.
        val = obj._expressions[name].eval()
        if not obj.initialized:
            obj.trait_setq(**{proxy_name: val})
        else:
            setattr(obj, proxy_name, val)

    def get(self, obj, name):
        """ Returns the value of the expression trait, initializing
        the attribute from the expression if necessary.

        """
        if not self.inited:
            # We need to flip the flag to True before initing the
            # expression since the act of evaluating the expression
            # may cause recursion into this get method which would
            # then infinitely recurse.
            self.inited = True
            self.init_expr(obj, name)
        return getattr(obj, self.proxy_name)

    def set(self, obj, name, val):
        """ Sets the value of the expression trait, initializing
        the attribute from the expression if necessary.

        """
        if not self.inited:
            # We need to flip the flag to True before initing the
            # expression since the act of evaluating the expression
            # may cause recursion into this get method which would
            # then infinitely recurse.
            self.inited = True
            self.init_expr(obj, name)
        setattr(obj, self.proxy_name, val)


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

    #: The private dictionary of expressions that are bound to attributes
    #: on this component. This should not normally be manipulated directly
    #: by the user. The bind_attribute method should be used instead.
    _expressions = Dict(Str, Instance(AbstractExpression))

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
    # Component Getters 
    #--------------------------------------------------------------------------
    def get_components(self):
        """ Returns the list of BaseComponent instance which should be
        included as proper children of our parent. By default this 
        simply returns [self]. This method should be reimplemented by 
        subclasses which need to contribute different components to their
        parent's children.

        """
        return [self]
    
    #--------------------------------------------------------------------------
    # Attribute Binding 
    #--------------------------------------------------------------------------
    def bind_expression(self, name, expression):
        """ Binds the given expression to the attribute 'name'. If
        the attribute does not exist, one is created.

        Parameters
        ----------
        name : string
            The name of the attribute on which to bind the expression.
        
        expression : AbstractExpression
            An implementation of enaml.expressions.AbstractExpression.
        
        init_quietly : bool, optional
            Whether or not to silence listeners when initializing the 
            value of the attribute from the expression. Defaults to True.
        
        """
        # The first time an expression is bound, we need to move the 
        # existing trait into its new shadow position. After that is
        # done, we create a new ExpressionTrait which points at the
        # shadow trait. A new ExpressionTrait is created each time
        # such that we support the desired behavior for initialization 
        # and notification.  
        self._expressions[name] = expression
        current_trait = self.trait(name)
        proxy_name = '_enaml_expr_trait_' + name

        # If this is the first time binding the expression, move the
        # current trait to its new proxy location.
        if current_trait is not None:
            if not isinstance(current_trait.trait_type, ExpressionTrait):
                self.add_trait(proxy_name, current_trait)
        # Otherwise, the user is requesting that we add a new attribute
        # on which we want to bind the expression.
        else:
            self.add_trait(proxy_name, Any())
        
        # Once the proxy is setup properly, we can add a new expression
        # trait at the given attribute location.
        expr_trait = ExpressionTrait(proxy_name)
        self.add_trait(name, expr_trait)

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
        4) Abstract objects bind their event handlers
        5) Abstract objects are added as a listeners to the shell object
        6) Visibility is initialized (toplevel nodes are skipped)
        7) Layout is initialized
        8) Nodes are marked as initialized

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
        before the 'initialized' attribute it set to True. By default, 
        this method is a no-op and should be reimplemented by subclasses 
        that need to perform some action for initializing the layout
        of themselves or their children.

        """
        self.initialize_layout()
        for child in self._subcomponents:
            child._setup_init_layout()

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

