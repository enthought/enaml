#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import deque
from itertools import izip_longest

from traits.api import (
    Bool, HasStrictTraits, Instance, List, Property, Str, WeakRef,
    cached_property, Event, on_trait_change
)

from .setup_hooks import AbstractSetupHook

from ..toolkit import Toolkit


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


class BaseComponent(HasStrictTraits):
    """ The most base class of the Enaml component heierarchy.

    All Enaml classes should inherit from this class. This class is not 
    meant to be used directly.

    """
    visible = Bool(True)

    #: The parent component of this component. It is stored as a weakref
    #: to mitigate issues with reference cycles. A top-level component's
    #: parent is None.
    parent = WeakRef('BaseComponent')

    #: The list of child for this component. This is read-only cached
    #: property that is computed based on the list of static children
    #: and the children contributed from any Include nodes.
    children = Property(List, depends_on='_subcomponents:_components_updated')

    #: The list of include nodes for this component.
    #: The toolkit specific object that implements the behavior of
    #: this component and manages the gui toolkit object. Subclasses
    #: should redefine this trait to specify the specialized type of
    #: abstract_obj that is accepted.
    abstract_obj = Instance(AbstractTkBaseComponent) 
    
    #: A list of hooks that are called during the setup process
    #: that can modify the behavior of the component such as installing
    #: listeners at the appropriate times.
    setup_hooks = List(Instance(AbstractSetupHook))

    #: A read-only property that returns the toolkit specific widget
    #: being managed by the abstract widget.
    toolkit_widget = Property

    #: Whether the component has been initialized or not. This will be 
    #: set to True after all of the setup() steps defined here are 
    #: completed. It should not be changed afterwards. This can be used 
    #: to trigger certain actions that need to be called after the 
    #: component has been set up.
    initialized = Bool(False)

    #: An optional name to give to this component to assist in finding
    #: it in the tree.
    name = Str

    #: A reference to the toolkit that created this object. This does 
    #: not need to be stored weakly because the toolkit does not maintain
    #: refs to the compoents that its constructors create.
    toolkit = Instance(Toolkit)
    
    #: The private internal list of sub components for this component. 
    #: This list should not be manipulated by the user, and should not 
    #: be changed after initialization.
    _subcomponents = List(Instance('BaseComponent'))

    #: A private event that should be emitted by a component when the 
    #: results of calling _get_compenents() has changed. This event is 
    #: listened to by the parent of subcomponents in order to know when 
    #: to rebuild its list of children. User code will not typically
    #: interact with this event.
    _components_updated = Event

    #--------------------------------------------------------------------------
    # Property and Component Getters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_children(self):
        """ The cached property getter for the 'children' attribute.

        This property getter returns the list of components in
        '_subcomponents' which are not instances of Include.

        """
        items = [item._get_components() for item in self._subcomponents]
        return sum(items, [])

    def _get_toolkit_widget(self):
        """ The property getter for the 'toolkit_widget' attribute.

        """
        return self.abstract_obj.toolkit_widget

    def _get_components(self):
        """ Returns the list of BaseComponent instance which should be
        included as proper children of our parent. By default this 
        simply returns [self]. This method should be overridden by 
        subclasses which need to contribute different components to their
        parent's children.

        """
        return [self]
    
    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def setup(self, parent=None):
        """ Run the setup process for the ui tree.

        The setup process is split into two phases: static and dynamic
        and each phase deals with the respective class of children.
        The static children are set up first, followed by the dynamic
        children. The reason for this order is that the static children
        must be first since its highly likely that the dynamic children
        will depend up the static children being properly initialized
        in order to operate correctly.

        The setup process for both the static and dynamic children
        is comprised of the following steps:
        
        1)  Child shell objects are given a reference to their parent
        2)  Setup hooks are initialized
        3)  Abstract objects create their internal toolkit object
        4)  Setup hooks are finalized
        5)  Abstract objects initialize their internal toolkit object
        6)  Abstract objects bind their event handlers
        7)  Setup hooks are bound
        8)  Abstract objects are added as a listeners to the shell object

        After these steps are completed, the following final steps are
        performed for all childrens:

        1) Layout is initialized
        2) Nodes are marked as initialized

        Each of the setup steps is performed in depth-first order. This 
        method should only be called on the root node of the tree.

        Parameters
        ----------
        parent : native toolkit widget, optional
            If embedding this BaseComponent into a non-Enaml GUI, use 
            this to pass the appropriate toolkit widget that should be 
            the parent for this component.

        """
        # Static Normal Children
        self._setup_parent_refs()
        self._setup_init_hooks()
        self._setup_create_widgets(parent)
        self._setup_final_hooks()
        self._setup_init_widgets()
        self._setup_bind_widgets()
        self._setup_bind_hooks()
        self._setup_listeners()
        self._setup_set_initialized()

        # Finalization
        self.initialize_layout()
    
    #--------------------------------------------------------------------------
    # Static Setup Methods 
    #--------------------------------------------------------------------------
    def _setup_parent_refs(self):
        """ A setup method which assigns the parent reference to the
        static children.

        """
        for child in self._subcomponents:
            child.parent = self
            child._setup_parent_refs()

    def _setup_init_hooks(self):
        """ A setup method which initializes the setup hooks.

        """
        for hook in self.setup_hooks:
            hook.initialize(self)
        for child in self._subcomponents:
            child._setup_init_hooks()

    def _setup_create_widgets(self, parent):
        """ A setup method that tells the abstract object to create its
        internal toolkit object.

        """
        self.abstract_obj.create(parent)
        self_widget = self.toolkit_widget
        for child in self._subcomponents:
            child._setup_create_widgets(self_widget)

    def _setup_final_hooks(self):
        """ A setup method which finalizes the setup hooks.

        """
        for hook in self.setup_hooks:
            hook.finalize(self)
        for child in self._subcomponents:
            child._setup_final_hooks()

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

    def _setup_bind_hooks(self):
        """ A setup method which binds the setup hooks.

        """
        for hook in self.setup_hooks:
            hook.bind(self)
        for child in self._subcomponents:
            child._setup_bind_hooks()

    def _setup_listeners(self):
        """ A setup method which sets the abstract object as a traits 
        listener for this component with a prefix of 'shell'.

        """
        self.add_trait_listener(self.abstract_obj, 'shell')
        for child in self._subcomponents:
            child._setup_listeners()

    def _setup_set_initialized(self):
        """ A setup method whic ets the initialized attribute to True.

        """
        self.initialized = True
        for child in self._subcomponents:
            child._setup_set_initialized()

    #--------------------------------------------------------------------------
    # Common Setup Methods
    #--------------------------------------------------------------------------
    def initialize_layout(self):
        """ A setup method called at the end of the setup process, but 
        before the 'initialized' attribute it set to True. By default, 
        this method is a no-op and should be reimplemented by subclasses 
        that need to perform some action for initializing the layout
        of themselves or their children.

        """
        for child in self.children:
            child.initialize_layout()

    def destroy(self):
        """ Destroys the underlying toolkit widget as well as all of
        the children of this component. After calling this method, the
        component and all of its children should be considered invalid
        and no longer used.

        """
        self.abstract_obj.destroy()
        for child in self.children:
            child.destroy()

    #--------------------------------------------------------------------------
    # Layout Stubs 
    #--------------------------------------------------------------------------
    def relayout(self):
        """ A method called after the dynamic children have changed and
        the new children have gone through the setup process. At the point
        this method is called, the ui tree will be in a consistent state,
        but the layout of the children will likely be incorrect. Any
        subclasses that manage layout should reimplement this method
        as needed in order to update the layout for the new children.

        """
        pass

    #--------------------------------------------------------------------------
    # Auxiliary Methods 
    #--------------------------------------------------------------------------
    def traverse(self, depth_first=False, node_attr='children'):
        """ Yields all of the nodes in the tree, from this node downward.

        Parameters
        ----------
        depth_first : bool, optional
            If True, yield the nodes in depth first order. If False,
            yield the nodes in breadth first order. Defaults to False.

        node_attr : string, optional
            The attribute on the nodes which will yield the child 
            nodes. Defaults to 'children'

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
            stack_extend(getattr(item, node_attr))

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


#------------------------------------------------------------------------------
# Null Toolkit Base Component
#------------------------------------------------------------------------------
class NullTkBaseComponent(AbstractTkBaseComponent):

    @property
    def toolkit_widget(self):
        return None

    _shell_obj = None

    def _get_shell_obj(self):
        return self._shell_obj
    
    def _set_shell_obj(self, val):
        pass
    
    shell_obj = property(_get_shell_obj, _set_shell_obj)

    def create(self, parent):
        pass
    
    def initialize(self):
        pass

    def bind(self):
        pass

    def destroy(self):
        pass


#------------------------------------------------------------------------------
# Include Component
#------------------------------------------------------------------------------
class Include(BaseComponent):
    """ A BaseComponent subclass which allows children to be dynamically
    inserted into a parent.

    """
    #: The dynamic list of items that should be included in our parent
    #: component. If this list changes dynamically at run time, then
    #: the old widgets will be destroyed and new ones will be inserted
    #: into the parent.
    items = List(Instance('BaseComponent'))
    
    #: A private Boolean flag indicating if the dynamic items of this 
    #: Include have been intialized for the first time. This should not 
    #: be manipulated directly by the user.
    _items_initialized = Bool(False)
    #: Overridden parent class trait which restricts an Include
    #: component to not have any subcomponents.
    _subcomponents = List(Instance('BaseComponent'), maxlen=0)

    #: Overridden parent class trait which restrict the type
    #: of the abstract object to the Null type.
    abstract_obj = Instance(NullTkBaseComponent)

    def _setup_items(self):
        """ An internal method used to setup the dynamic children.

        """
        items = self.items
        parent_shell = self.parent
        toolkit_parent = parent_shell.toolkit_widget
        
        for child in items:
            child.parent = parent_shell
            child._setup_parent_refs()
        
        for child in items:
            child._setup_init_hooks()
        
        for child in items:
            child._setup_create_widgets(toolkit_parent)
        
        for child in items:
            child._setup_final_hooks()
            
        for child in items:
            child._setup_init_widgets()

        for child in items:
            child._setup_bind_widgets()

        for child in items:
            child._setup_bind_hooks()
                
        for child in items:
            child._setup_listeners()

        for child in items:
            child._setup_set_initialized()

        self._items_initialized = True

    def _get_components(self):
        """ A reimplemented parent class method to include the dynamic
        children of this Include in our parent's list of children.

        """
        if self._items_initialized:
            # By calling _get_components here, we allow nested 
            # Includes to be expanded as expected.
            cmpnts = [item._get_components() for item in self.items]
            res = sum(cmpnts, [])
        else:
            res = []
        return res

    @on_trait_change('items:_components_updated')
    def handle_items_updated(self):
        """ Reacts to a change in the components updated event of the
        children items which proxies that change up to the parent.

        """
        # XXX we can probably do this more efficiently than just
        # trashing everything.
        print 'updated', self

    @on_trait_change('initialized')
    def handle_initialized(self, inited):
        """ Reacts to this component being fully initialized by the
        normal setup process. Once this Include object is fully 
        initialized, it is safe to create and setup the dynamic 
        children. This method runs that process when the 'initialized'
        flag is flipped from False to True.

        """
        if inited:
            self._setup_items()
            self._components_updated = True
    
    @on_trait_change('items[]')
    def handle_items_changed(self, obj, name, old, new):
        """ Reacts to changes in the items list and sets up the new list
        of children, making sure the parent is properly relayed out.

        """
        print 'items changed', self, new
        if self.initialized:
            # Old items must be destroyed before the new ones can be 
            # setup.
            for item in old:
                item.destroy()
            self._setup_items()
            self._components_updated = True
            self.parent.relayout()
    
    def destroy(self):
        for item in self.items:
            item.destroy()

