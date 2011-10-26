#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty
from functools import wraps

from traits.api import HasStrictTraits, WeakRef, Instance, List, Str

from .setup_hooks import AbstractSetupHook

from ..toolkit import Toolkit


class AbstractTkBaseComponent(object):
    """ The abstract toolkit BaseComponent interface.

    A toolkit BaseComponent is responsible for creating and initializing
    the state of its implementation and binding event handlers.

    """
    __metaclass__ = ABCMeta

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
    def create(self):
        """ Create the underlying implementation object. 

        This method is called after the reference to the shell object
        has been set and is called in depth-first order. This means
        that by the time this method is called, the logical parent
        of this instance has already been created.

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


def setup_hook(func):
    """ A decorator for methods involved in the setup process of a 
    BaseComponent tree. It handles the calling of the setup hooks at 
    the right places. The methods of a setup hook are generators that 
    can yield back to this decorator so that a single method can be 
    used to do pre- and post- processing of a setup method.

    """
    method_name = func.__name__
    
    @wraps(func)
    def closure(self, *args, **kwargs):
        # Create the generators from the setup hooks
        gens = [getattr(hook, method_name)(self) for hook in self.setup_hooks]

        # Iterate the generators to allow them to pre-process
        for gen in gens:
            gen.next()
        
        # Perform the setup operation
        func(self, *args, **kwargs)

        # Iterate the generators a second time to allow post-processing
        for gen in gens:
            try:
                gen.next()
            except StopIteration:
                pass

    return closure


class BaseComponent(HasStrictTraits):
    """ The most base class of the Enaml component heierarchy.

    All Enaml classes should inherit from this class. This class is not 
    meant to be used directly.

    """
    #: The parent component of this component. It is stored as a weakref
    #: to mitigate issues with reference cycles. A top-level component's
    #: parent is None.
    parent = WeakRef('BaseComponent')

    #: The list of children components for this component. Subclasses
    #: should redefine this trait to restrict which types of children
    #: they allow if necessary. This list should not be manipulated 
    #: outside of the ``*_child(...)`` methods so that the ui may be 
    #: properly updated when the children change.
    children = List(Instance('BaseComponent'))

    #: The toolkit specific object that implements the behavior of
    #: this component and manages the gui toolkit object. Subclasses
    #: should redefine this trait to specify the specialized type of
    #: abstract_obj that is accepted.
    abstract_obj = Instance(AbstractTkBaseComponent) 
    
    #: A list of hooks that are called during the setup process
    #: that can modify the behavior of the component such as installing
    #: listeners at the appropriate times. Hooks should normally be
    #: appended to this list instead of a list being assigned atomically.
    setup_hooks = List(Instance(AbstractSetupHook))

    #: The toolkit that created this object. This does not need to 
    #: be stored weakly because the toolkit does not maintain refs
    #: to the compoents that its constructors create.
    toolkit = Instance(Toolkit)

    #: The optional style identifier for the StyleSheet system.
    style_id = Str

    #: The optional style type for the StyleSheet system. This
    #: is set by default by the constructor object.
    style_type = Str

    #: The optional style class for the StyleSheet system.
    style_class = Str

    def add_child(self, child):
        """ Add the child to this component.

        Arguments
        ---------
        child : Instance(BaseComponent)
            The child to add to the component.

        """
        self.children.append(child)

    def remove_child(self, child):
        """ Remove the child from this component.

        Arguments
        ---------
        child : Instance(BaseComponent)
            The child to remove from the container.

        """
        try:
            self.children.remove(child)
        except ValueError:
            raise ValueError('Child %s not in children.' % child)

    def replace_child(self, child, other_child):
        """ Replace a child with another child.

        Arguments
        ---------
        child : Instance(BaseComponent)
            The child being replaced.

        other_child : Instance(BaseComponent)
            The child taking the place of the removed child.

        """
        try:
            idx = self.children.index(child)
        except ValueError:
            raise ValueError('Child %s not in children.' % child)
        self.children[idx] = other_child

    def swap_children(self, child, other_child):
        """ Swap the position of the two children.

        Arguments
        ---------
        child : Instance(BaseComponent)
            The first child in the swap.

        other_child : Instance(BaseComponent)
            The second child in the swap.

        """
        try:
            idx = self.children.index(child)
        except ValueError:
            raise ValueError('Child %s not in children.' % child)
        try:
            other_idx = self.children.index(other_child)
        except ValueError:
            raise ValueError('Child %s not in children.' % other_child)
        self.children[idx] = other_child
        self.children[other_idx] = child

    def set_style_sheet(self, style_sheet):
        """ Sets the style sheet for this component.

        Arguments
        ---------
        style_sheet : StyleSheet
            The style sheet instance for this component.

        """
        raise NotImplementedError('Implement me!')

    def setup(self):
        """ Run the setup process for the ui tree.

        This method splits up the setup process into several passes:
        
        1) The child shell objects are given a reference to their parent
        2) The abstract objects are given a reference to the shell object
        3) The abstract objects create their internal toolkit object
        4) The abstract objects initialize their internal toolkit object
        5) The abstract objects bind their event handlers
        6) The abstract object is added as a listener to the shell object

        Each of these methods are performed top down. Setup hooks are 
        called for items 3, 4, and 5.

        """
        self.set_parent_refs()
        self.set_shell_refs()
        self.create()
        self.initialize()
        self.bind()
        self.set_listeners()

    def set_parent_refs(self):
        """ Assigns a reference to self for every child in children and 
        dispatches the tree top down. This should not normally be called 
        by user code.

        """
        for child in self.children:
            child.parent = self
            child.set_parent_refs()

    def set_shell_refs(self):
        """ Assigns a reference to self to the abstract obj and 
        dispatches the tree top down. This should not normally be 
        called by user code.

        """
        self.abstract_obj.shell_obj = self
        for child in self.children:
            child.set_shell_refs()
        
    @setup_hook
    def create(self):
        """ A setup method that tells the abstract object to create its
        internal toolkit object. This should not normally be called by 
        user code.

        """
        self.abstract_obj.create()
        for child in self.children:
            child.create()

    @setup_hook
    def initialize(self):
        """ A setup method that tells the abstract object to initialize
        its internal toolkit object. This should not normally be called 
        by user code.

        """
        self.abstract_obj.initialize()
        for child in self.children:
            child.initialize()

    @setup_hook
    def bind(self):
        """ A setup method that tells the abstract object to bind its
        event handlers to its internal toolkit object. This should not
        normally be called by user code.

        """
        self.abstract_obj.bind()
        for child in self.children:
            child.bind()

    def set_listeners(self):
        """ Sets the abstract object as a traits listener for this
        component with a prefix of 'shell'.

        """
        self.add_trait_listener(self.abstract_obj, 'shell')
        for child in self.children:
            child.set_listeners()

