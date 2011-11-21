#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty
from functools import wraps

from traits.api import (
    Bool, HasStrictTraits, Instance, List, Property, Str, Tuple, WeakRef,
)

from .setup_hooks import AbstractSetupHook

from ..styling.color import ColorTrait
from ..styling.font import FontTrait
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

    @abstractmethod
    def shell_enabled_changed(self, enabled):
        """ The change handler for the 'enabled' attribute on the shell
        object. Sets the enabled/disabled state of the widget.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_visible_changed(self, visible):
        """ The change handler for the 'visible' attribute on the shell
        object. Sets the visibility state of the widget.

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


class NullContext(object):
    """ A do-nothing context object that is created by the __call__
    method of SetupContext when that context is being used by a 
    non-toplevel call.

    """
    def __enter__(self):
        pass
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        pass


class SetupContext(object):
    """ A context object that will compute and run a set of generators
    before and after yielding control to user code. An instance of this
    context manager cannot be entered recursively.

    """
    def __init__(self, method_name):
        """ Initialize a SetupContext.

        Parameters
        ----------
        method_name : string
            The name of the method on the setup hooks to call in order
            to create the setup generators.

        """
        self.method_name = method_name
        self.component = None
        self.gens = None

    def __call__(self, component):
        """ Prime the context manager for use.

        Parameters
        ----------
        component : Instance(BaseComponent)
            A component which has SetupHooks installed.

        Returns
        -------
        result : NullContext or self.
            If this manager is not in use, it will be primed and 
            returned, otherwise a NullContext instance will be returned.

        """
        if self.component is not None:
            return NullContext()
        self.component = component
        return self

    def __enter__(self):
        """ Collects the setuphook generators for the tree starting at
        the current node and iterates the generators as a pre-processing
        step.

        """
        # Walk the tree of components from this point down and collect
        # a flat list of all of the setup hook generators.
        gens = []
        gens_extend = gens.extend
        stack = [self.component]
        stack_extend = stack.extend
        stack_pop = stack.pop
        while stack:
            cmpnt = stack_pop()
            gens_extend((getattr(hook, self.method_name)(cmpnt) 
                         for hook in cmpnt.setup_hooks))
            stack_extend(cmpnt.children)
        
        # Iterate the generators as a pre-processing step
        for gen in gens:
            gen.next()
        
        # Store the generators until the exit method, 
        # so they can be iterated a second time.
        self.gens = gens
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        """ Iterates the collected generates a second time as a post
        processing step, provided that the user code did not raise 
        any exceptions.

        """
        # The user functions have now already run, and possibly
        # raised an exception. In any case, we need to reset the
        # internal state of this context manager and then iterate
        # the generators a second time if no exception was raise
        # by the user code.
        self.component = None
        gens = self.gens
        self.gens = None
        if exc_type is None:
            for gen in gens:
                try:
                    gen.next()
                except StopIteration:
                    pass


def setup_hook(func):
    """ A decorator for methods involved in the setup process of a 
    BaseComponent tree. It handles the calling of the setup hooks at 
    the right places. The methods of a setup hook are generators that 
    can yield back to this decorator so that a single method can be 
    used to do pre- and post- processing of a setup method.

    """
    setup_context = SetupContext(func.__name__)

    @wraps(func)
    def closure(self, *args, **kwargs):
        with setup_context(self):
            func(self, *args, **kwargs)

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

    #: Whether or not the widget is enabled.
    enabled = Bool(True)

    #: Whether or not the widget is visible.
    visible = Bool(True)

    #: The background color of the widget
    bg_color = Property(ColorTrait, depends_on=['_user_bg_color', '_style_bg_color'])
    
    #: Private trait holding the user-set background color value
    _user_bg_color = ColorTrait
    
    #: Private trait holding the background color value from the style
    _style_bg_color = ColorTrait

    #: The foreground color of the widget
    fg_color = Property(ColorTrait, depends_on=['_user_fg_color', '_style_fg_color'])
    
    #: Private trait holding the user-set foreground color value
    _user_fg_color = ColorTrait
    
    #: Private trait holding the foreground color value from the style
    _style_fg_color = ColorTrait

    #: The foreground color of the widget
    font = Property(FontTrait, depends_on=['_user_font', '_style_font'])
    
    #: Private trait holding the user-set foreground color value
    _user_font = FontTrait
    
    #: Private trait holding the foreground color value from the style
    _style_font = FontTrait

    #: The attributes on this class that can be set by the styling mechanism
    _style_tags = Tuple(Str, ('bg_color', 'fg_color', 'font'))
 
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

    def _set_bg_color(self, new):
        """ Property setter for the 'bg_color' background color property.
        Set values are pushed to the '_user_bg_color' trait.
        """
        self._user_bg_color = new
    
    def _get_bg_color(self):
        """ Property sgtter for the 'bg_color' background color property.
        We use the '_user_bg_color' trait unless it is None.
        """
        if self._user_bg_color:
            return self._user_bg_color
        return self._style_bg_color

    def _set_fg_color(self, new):
        """ Property setter for the 'fg_color' foreground color property.
        Set values are pushed to the '_user_fg_color' trait.
        """
        self._user_fg_color = new
    
    def _get_fg_color(self):
        """ Property sgtter for the 'fg_color' foreground color property.
        We use the '_user_fg_color' trait unless it is None.
        """
        if self._user_fg_color:
            return self._user_fg_color
        return self._style_fg_color

    def _set_font(self, new):
        """ Property setter for the 'fg_color' foreground color property.
        Set values are pushed to the '_user_fg_color' trait.
        """
        self._user_font = new
    
    def _get_font(self):
        """ Property sgtter for the 'fg_color' foreground color property.
        We use the '_user_fg_color' trait unless it is None.
        """
        if self._user_font:
            return self._user_font
        return self._style_font

