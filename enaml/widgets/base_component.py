#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import deque, namedtuple

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
    def create(self, parent):
        """ Create the underlying implementation object. 

        This method is called after the reference to the shell object
        has been set and is called in depth-first order. This means
        that by the time this method is called, the logical parent
        of this instance has already been created.

        Parameters
        ----------
        parent : toolkit widget or None
            The toolkit widget that will be the parent for widget.

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


DelegateEntry = namedtuple('DelegateEntry', 'idx delegate')


class BaseComponent(HasStrictTraits):
    """ The most base class of the Enaml component heierarchy.

    All Enaml classes should inherit from this class. This class is not 
    meant to be used directly.

    """
    #: The parent component of this component. It is stored as a weakref
    #: to mitigate issues with reference cycles. A top-level component's
    #: parent is None.
    parent = WeakRef('BaseComponent')

    #: A readonly property which returns a list of children for this 
    #: component. The list will contain any children that are created
    #: by Delegate leaves.
    children = List(Instance('BaseComponent'))

    #: The private list of children components for this component. A
    #: subclass should redefine this trait as necessary to restrict 
    #: which types of children they allow. This list should not be
    #: manipulated directly so that the tree can be properly updated
    #: when the children or delegates change.
    #_children = List(Instance('BaseComponent'))

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

    #: Whether the component has been initialized for not. This will be set to
    #: True after all of the setup() steps defined here are completed. It should
    #: not be changed afterwards. This can be used to trigger certain actions
    #: that need to be called after the component has been set up.
    initialized = Bool(False)

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

    #: An optional name to give to this component to assist in finding
    #: it in the tree.
    name = Str

    def add_child(self, child):
        """ Add the child to this component.

        Arguments
        ---------
        child : Instance(BaseComponent)
            The child to add to the component.

        """
        self.children.append(child)

    def traverse(self):
        """ Yields all of the nodes in the tree in breadth first order.

        """
        deq = deque([self])
        while deq:
            item = deq.popleft()
            yield item
            deq.extend(item.children)
    
    def find_by_name(self, name):
        """ Find a component in this tree by name. 

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

    def set_style_sheet(self, style_sheet):
        """ Sets the style sheet for this component.

        Arguments
        ---------
        style_sheet : StyleSheet
            The style sheet instance for this component.

        """
        raise NotImplementedError('Implement me!')

    def setup(self, parent=None):
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

        After step 6, the `initialized` trait is set to True.

        Parameters
        ----------
        parent : native toolkit widget, optional
            If embedding this BaseComponent into a non-Enaml GUI, use this
            to pass the appropriate toolkit widget that should be the parent.

        """
        self.initialize_hooks()
        self.set_parent_refs()
        self.set_shell_refs()
        self.create(parent)
        self.finalize_hooks()
        self.initialize()
        self.bind()
        self.bind_hooks()
        self.set_listeners()
        self.initialized = True

    def initialize_hooks(self):
        """ A setup hook method which is the very first method called
        during the setup process. The hook should make their expressions
        available for use at this time.

        """
        for hook in self.setup_hooks:
            hook.initialize(self)
        for child in self.children:
            child.initialize_hooks()
    
    def finalize_hooks(self):
        """ A setup hook method which is called after all of the widgets
        in the tree have been created.

        """
        for hook in self.setup_hooks:
            hook.finalize(self)
        for child in self.children:
            child.finalize_hooks()
    
    def bind_hooks(self):
        """ A setup hook method which is called after all of the event
        handlers for the toolkit widgets have been bound.

        """
        for hook in self.setup_hooks:
            hook.bind(self)
        for child in self.children:
            child.bind_hooks()

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
        
    def create(self, parent):
        """ A setup method that tells the abstract object to create its
        internal toolkit object. This should not normally be called by 
        user code.

        """
        self.abstract_obj.create(parent)
        # FIXME: toolkit_widget is defined on Component, not BaseComponent.
        # FIXME: technically, we allow toolkit_widget to be something that is
        # not precisely a real toolkit widget (e.g. a QLayout).
        self_widget = self.toolkit_widget
        for child in self.children:
            child.create(self_widget)

    def initialize(self):
        """ A setup method that tells the abstract object to initialize
        its internal toolkit object. This should not normally be called 
        by user code.

        """
        self.abstract_obj.initialize()
        for child in self.children:
            child.initialize()

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

