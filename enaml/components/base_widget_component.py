#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty

from traits.api import Property, Instance

from ..core.base_component import BaseComponent


class AbstractTkBaseWidgetComponent(object):
    """ The abstract toolkit BaseWidgetComponent interface.

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


#------------------------------------------------------------------------------
# BaseWidgetComponent
#------------------------------------------------------------------------------
class BaseWidgetComponent(BaseComponent):
    """ A BaseComponent subclass which adds support for a gui toolkit 
    specific backend object. This class represents the most basic 
    component in Enaml that drives a gui toolkit object. The gui toolkit 
    object at this level is not necessarily a widget which can paint on
    the screen.

    """
    #: A read-only property that returns the toolkit specific widget
    #: being managed by the abstract widget.
    toolkit_widget = Property

    #: The toolkit specific object that implements the behavior of
    #: this component and manages the gui toolkit object. Subclasses
    #: should redefine this trait to specify the specialized type of
    #: abstract_obj that is accepted.
    abstract_obj = Instance(AbstractTkBaseWidgetComponent)

    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    def _get_toolkit_widget(self):
        """ The property getter for the 'toolkit_widget' attribute.

        """
        return self.abstract_obj.toolkit_widget
    
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def _setup_create_widgets(self, parent):
        """ A reimplemented parent class setup method which creates the
        underlying toolkit widgets.

        """
        self.abstract_obj.create(parent)
        self_widget = self.toolkit_widget
        super(BaseWidgetComponent, self)._setup_create_widgets(self_widget)

    def _setup_init_widgets(self):
        """ A reimplemented parent class setup method which initializes
        the underyling toolkit widgets.

        """
        self.abstract_obj.initialize()
        super(BaseWidgetComponent, self)._setup_init_widgets()
    
    def _setup_bind_widgets(self):
        """ A reimplemented parent class setup method which binds the
        event handlers for the internal toolkit widgets.

        """
        self.abstract_obj.bind()
        super(BaseWidgetComponent, self)._setup_bind_widgets()
    
    def _setup_listeners(self):
        """ A reimplemented parent class setup method which sets up
        the trait listeners for the abstract object.

        """
        self.add_trait_listener(self.abstract_obj, 'shell')
        super(BaseWidgetComponent, self)._setup_listeners()

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
        super(BaseWidgetComponent, self).destroy()
        
        # On pass back up the tree, destroy the abstract_obj.
        self.abstract_obj.destroy()
        self.abstract_obj = None

