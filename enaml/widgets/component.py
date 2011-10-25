#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty
from functools import wraps

from traits.api import HasStrictTraits, Str, WeakRef, Instance, List, ReadOnly, Property

from .setup_hooks import AbstractSetupHook


class AbstractTkComponent(object):
    """ The abstract toolkit Component interface.

    A toolkit component is responsible for handling changes on a shell 
    widtget and doing conversions to and from those attributes and values 
    on a toolkit widget.

    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def shell_widget(self):
        """ An abstract property that should *get* and *set* a reference
        to the shell widget (an instance of Component). 

        It is suggested that the implementation maintain only a weakref
        to the shell widget in order to avoid reference cycles. This 
        value will be set by the framework before any other widget 
        creation or layout methods are called. It is performed in depth
        first order

        """
        raise NotImplementedError
    
    @abstractproperty
    def toolkit_widget(self):
        """ An abstract property that should return the gui toolkit 
        widget being managed by the instance.

        """
        raise NotImplementedError

    @abstractmethod
    def create_widget(self):
        """ Create the underlying toolkit widget. 

        This method is called after the reference to the shell widget 
        has been set and is called in depth-first order. This means
        that by the time this method is called, the logical parent
        of widget of this instance has already been created.

        """
        raise NotImplementedError
    
    @abstractmethod
    def initialize_widget(self):
        """ Initializes the widget with attributes from the parent.

        This method is called after 'create_widget' in depth-first
        order.

        """
        raise NotImplementedError

    @abstractmethod
    def initialize_layout(self):
        """ Initializes any required layout information for the widget
        and/or its children.

        This method is called after 'initialize_widget' in depth-first
        order.

        """
        raise NotImplementedError

    @abstractmethod
    def initialize_event_handlers(self):
        """ After the ui tree is fully initialized, this method
        is called to allow the widgets to bind their event handlers.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_name_changed(self, name):
        """ Called when the name attribute of the shell widget changes.

        The value of the name attribute can be used for various things
        in a ui, such as the names of the tabs in a notebook, or the
        values of the labels in a form layout.

        """
        raise NotImplementedError


def setup_method(func):
    """ A decorator for methods involved in the setup process of a 
    component tree. It handles the depth first dispatching and 
    calling of the setup hooks.

    """
    method_name = func.__name__
    
    @wraps(func)
    def closure(self):
        # Call the pre-process hooks
        gens = [getattr(hook, method_name)(self) for hook in self.setup_hooks]
        for gen in gens:
            gen.next()
        
        # Perform the setup operation
        func(self)

        # Run the same process for the children, the insures that
        # func(self) is called for every item in the tree before 
        # the first post-process hook is run.
        for child in self.children:
            getattr(child, method_name)()

        # Call the post-process hooks
        for gen in gens:
            try:
                gen.next()
            except StopIteration:
                pass

    return closure


class Component(HasStrictTraits):
    """ The most base class of the Enaml widgets component heierarchy.

    All Enaml  widget classes should inherit from this class. This class
    is not meant to be used directly.

    """
    #: The parent component of this component. It is stored as a weakref
    #: to mitigate issues with reference cycles. A top-level component's
    #: parent is None.
    parent = WeakRef('Component')

    #: The identifier assigned to this element in the enaml source code.
    identifier = ReadOnly

    # XXX handle this better than being set by the toolkit
    type_name = ReadOnly

    #: The name of this element which may be used as metainfo by other
    #: components. Note that this is not the same as the identifier
    #: that can be assigned to a component as part of the enaml grammar.
    name = Str

    #: The list of children components for this component. Subclasses
    #: should redefine this trait to restrict which types of children
    #: they allow. This list should not be manipulated outside of
    #: the ``*_child(...)`` methods so that the ui may be properly 
    #: updated when the children change. Note that a Component does
    #: not accept children, but the attribute and methods are defined
    #: on the component to formalize the interface for subclasses.
    children = List(Instance('Component'), maxlen=0)

    #: The toolkit specific object that implements the behavior of
    #: this component and manages the gui toolkit widget. Subclasses
    #: should redefine this trait to specify the specialized type of
    #: abstract_widget that is accepted.
    abstract_widget = Instance(AbstractTkComponent) 
    
    #: A list of hooks that are called during the setup process
    #: that can modify the behavior of the component such as installing
    #: listeners at the appropriate times. Hooks should normally be
    #: appended to this list instead of it being assigned atomically
    setup_hooks = List(Instance(AbstractSetupHook))

    #: A read-only property that returns the gui toolkit widget
    #: being managed by the abstract widget.
    toolkit_widget = Property

    def add_child(self, child):
        """ Add the child to this component. Subclasses that support
        children *must* implement this method.

        Arguments
        ---------
        child : Instance(Component)
            The child to add to the component.

        """
        raise NotImplementedError

    def remove_child(self, child):
        """ Remove the child from this component. Subclasses that support
        children *should* implement this method.

        Arguments
        ---------
        child : Instance(Component)
            The child to remove from the container.

        """
        raise NotImplementedError

    def replace_child(self, child, other_child):
        """ Replace a child with another child. Subclasses that support
        children *should* implement this method.

        Arguments
        ---------
        child : Instance(Component)
            The child being replaced.

        other_child : Instance(Component)
            The child taking the place of the removed child.

        """
        raise NotImplementedError

    def swap_children(self, child, other_child):
        """ Swap the position of the two children. Subclasses that 
        support children *should* implement this method.

        Arguments
        ---------
        child : Instance(Component)
            The first child in the swap.

        other_child : Instance(Component)
            The second child in the swap.

        """
        raise NotImplementedError

    def set_style_sheet(self, style_sheet):
        """ Sets the style sheet for this component.

        Arguments
        ---------
        style_sheet : StyleSheet
            The style sheet instance for this component.

        """
        self.style.style_sheet = style_sheet

    def setup(self):
        """ Initialize and arrange the component and it's children.

        This method dispatches the setup process into several passes 
        across the ui tree.

        """
        self.parent_children()
        self.set_shell_widget()
        self.create_widget()
        self.initialize_widget()
        self.initialize_layout()  
        self.initialize_event_handlers()
        self.set_abstract_widget_listeners()

    @setup_method
    def parent_children(self):
        """ A setup method that sets the parent attribute of the children
        of this component. This should not normally be called by user
        code.

        """
        for child in self.children:
            child.parent = self

    @setup_method
    def set_shell_widget(self):
        """ A setup method that sets the shell widget attribute of the
        abstract widget. This should not normally be called by user
        code.

        """
        self.abstract_widget.shell_widget = self
        
    @setup_method
    def create_widget(self):
        """ A setup method that tells the abstract widget to create its
        gui toolkit widget. This should not normally be called by user
        code.

        """
        self.abstract_widget.create_widget()
    
    @setup_method
    def initialize_widget(self):
        """ A setup method that tells the abstract widget to initialize
        its gui toolkit widget. This should not normally be called by 
        user code.

        """
        self.abstract_widget.initialize_widget()

    @setup_method
    def initialize_layout(self):
        """ A setup method that tells the abstract widget to initialize
        its layout. This should not normally be called by user code.

        """
        self.abstract_widget.initialize_layout()

    @setup_method
    def initialize_event_handlers(self):
        """ After the ui tree is fully initialized, this method
        is called to allow the widgets to bind their event handlers.

        """
        self.abstract_widget.initialize_event_handlers()

    @setup_method
    def set_abstract_widget_listeners(self):
        """ Sets the abstract_widget as a traits listener for this
        component with a prefix of 'shell'.

        """
        self.add_trait_listener(self.abstract_widget, 'shell')

    def _get_toolkit_widget(self):
        """ The getter for the toolkit_widget property.

        """
        return self.abstract_widget.toolkit_widget

