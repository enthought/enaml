#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty

from traits.api import Instance, Property, Bool

from ..core.base_component import BaseComponent
from ..guard import guard


#------------------------------------------------------------------------------
# Freeze Context
#------------------------------------------------------------------------------
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


#------------------------------------------------------------------------------
# Abstract Toolkit Component Interface
#------------------------------------------------------------------------------
class AbstractTkComponent(object):
    """ The abstract toolkit Component interface.

    A toolkit component is responsible for handling changes on a shell 
    Component and proxying those changes to and from its internal guit
    toolkit widget.

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
        to the shell object (an instance of Component). 

        It is suggested that the implementation maintain only a weakref
        to the shell object in order to avoid reference cycles.

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

        Rather than raise the more typical NotImplementedError, this
        abstractmethod is no-op so that implementors with complex
        multiple inheritence heierarhies can use super() all the 
        way to the top.

        """
        pass

    @abstractmethod
    def bind(self):
        """ Called after 'initialize' in order to bind event handlers.

        At the time this method is called, the entire tree of ui
        objects will have been initialized. The intention of this 
        method is delay the binding of event handlers until after
        everything has been intialized in order to mitigate extraneous
        event firing.

        Rather than raise the more typical NotImplementedError, this
        abstractmethod is no-op so that implementors with complex
        multiple inheritence heierarhies can use super() all the 
        way to the top.

        """
        pass

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
        """ The change handler for the 'enabled' attribute of the shell
        object. Sets the widget enabled according to the given boolean.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Enaml Component
#------------------------------------------------------------------------------
class Component(BaseComponent):
    """ A BaseComponent subclass that adds support for a toolkit specific
    abstract object. This class represents the most basic widget in Enaml
    that drives a gui toolkit widget.

    """
    #: Whether or not the widget is enabled.
    enabled = Bool(True)

    #: Whether or not the widget is visible.
    visible = Bool(True)

    #: A property which returns whether or not this component is 
    #: currently frozen.
    frozen = Property

    #: A read-only property that returns the toolkit specific widget
    #: being managed by the abstract widget.
    toolkit_widget = Property

    #: The toolkit specific object that implements the behavior of
    #: this component and manages the gui toolkit object. Subclasses
    #: should redefine this trait to specify the specialized type of
    #: abstract_obj that is accepted.
    abstract_obj = Instance(AbstractTkComponent) 

    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    def _get_toolkit_widget(self):
        """ The property getter for the 'toolkit_widget' attribute.

        """
        return self.abstract_obj.toolkit_widget

    def _get_frozen(self):
        """ The property getter for the 'frozen' attribute.

        """
        return FreezeContext.is_frozen(self)

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def _setup_create_widgets(self, parent):
        """ A reimplemented parent class setup method which creates the
        underlying toolkit widgets.

        """
        self.abstract_obj.create(parent)
        self_widget = self.toolkit_widget
        super(Component, self)._setup_create_widgets(self_widget)

    def _setup_init_widgets(self):
        """ A reimplemented parent class setup method which initializes
        the underyling toolkit widgets.

        """
        self.abstract_obj.initialize()
        super(Component, self)._setup_init_widgets()
    
    def _setup_bind_widgets(self):
        """ A reimplemented parent class setup method which binds the
        event handlers for the internal toolkit widgets.

        """
        self.abstract_obj.bind()
        super(Component, self)._setup_bind_widgets()
    
    def _setup_listeners(self):
        """ A reimplemented parent class setup method which sets up
        the trait listeners for the abstract object.

        """
        self.add_trait_listener(self.abstract_obj, 'shell')
        super(Component, self)._setup_listeners()
    
    def _setup_init_visibility(self):
        """ A reimplemented parent class setup method which initializes
        the visibility of the component.

        """
        self.set_visible(self.visible)
        super(Component, self)._setup_init_visibility()
        
    #--------------------------------------------------------------------------
    # Teardown Methods
    #--------------------------------------------------------------------------
    def destroy(self):
        """ Overridden parent class destruction method method that adds 
        additional logic to destroy the underlying toolkit widget. 

        The destruction happens in dual pass top-down, then bottom-up.
        On the top-down pass, the traits listeners for the abstract obj
        are unhooked so that no events get fired during destruction. On
        the bottom up pass, the abstract obj is destroyed and its ref
        set to None.

        """
        # Remove the abstract object as a trait listener so that it
        # does not try to update after destroying its internal widget.
        self.remove_trait_listener(self.abstract_obj, 'shell')

        # Traverse down the tree and have the children destroy themselves.
        super(Component, self).destroy()
        
        # On pass back up the tree, destroy the abstract_obj.
        self.abstract_obj.destroy()
        self.abstract_obj = None
    
    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
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
        boolean. Subclasses that need more control over visibility
        changes should reimplement this method.

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
        
        # Only set the visibility of the component if it is fully 
        # initialized or being set to False. This prevents situations 
        # where a widget is shown prematurely in some toolkit backends
        # which then causes the entire window hierarchy to be shown
        # prematurely.
        if self.initialized or not visible:
            self.abstract_obj.set_visible(visible)

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
        nested.

        """
        return FreezeContext(self)

