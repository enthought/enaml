#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref

from traits.api import (
    List, Instance, Bool, on_trait_change, Property, cached_property, Any,
)

from .base_component import BaseComponent, AbstractTkBaseComponent


class NullTkInclude(AbstractTkBaseComponent):
    """ A null toolkit Include implementation. An Include object does
    not need an abstract object implementation, so this class is just
    a null implementation of the required interface.

    """
    @property
    def toolkit_widget(self):
        return None

    _shell_obj = lambda self: None

    def _get_shell_obj(self):
        return self._shell_obj()
    
    def _set_shell_obj(self, val):
        self._shell_obj = weakref.ref(val)
    
    shell_obj = property(_get_shell_obj, _set_shell_obj)

    def create(self, parent):
        pass
    
    def initialize(self):
        pass

    def bind(self):
        pass

    def destroy(self):
        pass
    
    def disable_updates(self):
        pass
    
    def enable_updates(self):
        pass
    
    def shell_enabled_changed(self, enabled):
        pass

    def shell_bg_color_changed(self, color):
        pass
    
    def shell_fg_color_changed(self, color):
        pass
    
    def shell_font_changed(self, font):
        pass

    def set_visible(self, visible):
        pass


class Include(BaseComponent):
    """ A BaseComponent subclass which allows children to be dynamically
    included into a parent.

    """
    #: The dynamic components of the Include. This is a cached property
    #: which will convert a variety of inputs into an appropriate list
    #: that is stored internally. Allowable values and their converted
    #: values are as follows:
    #:     None -> []
    #:     component -> [component]
    #:     [components] -> [components]
    components = Property(Any, depends_on='_components')
        
    #: A private attribute which stores the underlying list of created
    #: components. This list should not be manipulated by user code.
    _components = List(Instance(BaseComponent))

    #: A private Boolean flag indicating if the dynamic components of 
    #: this Include have been intialized for the first time. This should 
    #: not be manipulated directly by the user.
    _components_initialized = Bool(False)

    #: An Overridden parent class trait which restricts this Include 
    #: component to not have any static subcomponents.
    _subcomponents = List(Instance('BaseComponent'), maxlen=0)

    #: An Overridden parent class trait which restrict the type of the
    #: abstract object to be a NullTkInclude type.
    abstract_obj = Instance(NullTkInclude)

    #--------------------------------------------------------------------------
    # Property Getters and Setters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_components(self):
        """ The cached property getter for the 'components' attribute. It
        simply returns the private '_components' list.

        """
        return self._components
    
    def _set_components(self, val):
        """ The property setter for the 'components' attribut. It 
        converts a variety of acceptable values into a list that is 
        stored in the '_components' attribute.

        """
        if val is None:
            val = []
        elif isinstance(val, BaseComponent):
            val= [val]
        self._components = val

    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def _setup_components(self):
        """ An internal method used to setup the dynamic child components.

        """
        cmpnts = self.components
        if not cmpnts:
            return

        # The dynamic components of an Include are injected into the 
        # parent's children inline so that they *appear* as if they
        # are siblings of the Include. To do this, we pass the reference
        # to the parent of the Include and the corresponding toolkit
        # widget where appropriate.
        parent_shell = self.parent
        toolkit_parent = parent_shell.toolkit_widget
        
        # The following blocks perform roughly the same setup process
        # as BaseComponent.setup(), except that we don't need to perform
        # the setup for this Include instance (since it's already) setup.
        # Also, since we don't need to recurse into any children (an
        # Include can't have children), there is no need to break these
        # blocks out into separate methods.
        for child in cmpnts:
            child.parent = parent_shell
            child._setup_parent_refs()
        
        for child in cmpnts:
            child._setup_create_widgets(toolkit_parent)
            
        for child in cmpnts:
            child._setup_init_widgets()

        for child in cmpnts:
            child._setup_bind_widgets()
                
        for child in cmpnts:
            child._setup_listeners()

        for child in cmpnts:
            child._setup_init_visibility()

        for child in cmpnts:
            child._setup_init_layout()

        for child in cmpnts:
            child._setup_set_initialized()

        self._components_initialized = True

    #--------------------------------------------------------------------------
    # Parent Class Overrides 
    #--------------------------------------------------------------------------
    def get_components(self):
        """ A reimplemented parent class method to include the dynamic
        children of this Include in our parent's list of children.

        """
        if self._components_initialized:
            res = sum([c.get_components() for c in self.components], [])
        else:
            res = []
        return res

    def destroy(self):
        """ A re-implemented parent class method which destroys all of
        the underlying dynamic children.

        """
        for item in self.components:
            item.destroy()

    def freeze(self):
        """ A re-implemented parent class method which returns the 
        freeze context of the parent of the include, since an Include
        has no toolkit widget on which to disable updates.

        """
        return self.parent.freeze()

    #--------------------------------------------------------------------------
    # Change Handlers 
    #--------------------------------------------------------------------------
    @on_trait_change('initialized')
    def _handle_initialized(self, inited):
        """ Reacts to this component being fully initialized by the
        normal setup process. Once this Include is fully initialized, 
        it is safe to create and setup the dynamic children. This method
        runs that process when the 'initialized' flag is flipped from 
        False to True and then fires the '_components_updated' event.

        """
        if inited:
            self._setup_components()
            # Since the initial list of components may be assigned during
            # a trait_setq context (by the Enaml expression binders) the
            # items listeners don't get hooked up if we use the trait
            # change method decorator. Instead, we manually bind the 
            # notifier the first time this component is initialized.
            self.on_trait_change(self._on_subcomponents_updated, 
                                 '_components:_components_updated')
            self._components_updated = True
    
    @on_trait_change('components')
    def _handle_components_changed(self, obj, name, old, new):
        """ Reacts to changes in the dynamic components and sets up the 
        new children, making sure the old ones are destroyed and that the
        '_components_updated' event gets fired.

        """
        if self.initialized:
            def closure():
                for item in old:
                    item.destroy()
                self._setup_components()
                self._components_updated = True
            self.relayout_enqueue(closure)
            
    # This notifier is hooked up in the '_handle_initialized' method 
    # due to issues surrounding trait_setq contexts.
    def _on_subcomponents_updated(self):
        """ Handles a '_components_updated' event being fired by one 
        the dynamic components. The event is proxied up the tree by
        firing the same event on this instance. This allows a nested
        Include to update its contents independent of the Include in
        which it is nested.

        """        
        self._components_updated = True

