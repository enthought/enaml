#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import List, Instance, Either, Bool, Property, cached_property

from ..core.base_component import BaseComponent


class Include(BaseComponent):
    """ A BaseComponent subclass which allows children to be dynamically
    included into a parent.

    """
    #: A read-only property which returns the toolkit widget for this
    #: component. This call is proxied to the parent and will return
    #: None if the parent does not have a toolkit widget defined. 
    #: It is necessary to proxy the toolkit_widget so that any child
    #: Include components can access the proper toolkit widget to 
    #: pass down to their dynamic components.
    toolkit_widget = Property

    #: The dynamic components of the Include. This is a cached property
    #: which will accept a single component, or a list of components as
    #: input. If the input is a single component, it will be converted
    #: into a single element list.
    components = Property(
        Either(List(Instance(BaseComponent)), Instance(BaseComponent)),
        depends_on='_components',
    )
    
    #: A private attribute which stores the underlying list of created
    #: components. This list should not be manipulated by user code.
    _components = List(Instance(BaseComponent))

    #: A private Boolean flag indicating if the dynamic components of 
    #: this Include have been intialized for the first time. This should 
    #: not be manipulated directly by the user.
    _components_initialized = Bool(False)

    #--------------------------------------------------------------------------
    # Property Getters and Setters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_components(self):
        """ The cached property getter for the 'components' attribute. 
        It simply returns the private '_components' list.

        """
        return self._components
    
    def _set_components(self, val):
        """ The property setter for the 'components' attribute. It will
        convert a single component into a single element list.

        """
        if isinstance(val, BaseComponent):
            val = [val]
        self._components = val
    
    def _get_toolkit_widget(self):
        """ The property getter for the 'toolkit_widget' attribute.

        """
        try:
            res = self.parent.toolkit_widget
        except AttributeError:
            res = None
        return res

    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def _setup_init_layout(self):
        """ A reimplemented parent class method which builds the initial
        list of include components during the layout initialization pass.
        The layout is performed bottom-up so that the tree is up-to-date
        before any parents compute their layout.

        """
        super(Include, self)._setup_init_layout()
        self._setup_components()
        self.on_trait_change(
            self._on_components_actual_updated, '_components:_actual_updated',
        )
        self._actual_updated()

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
        parent = self.parent
        try:
            # If our parent is a BaseComponent, it won't have a 
            # toolkit_widget attribute.
            toolkit_parent = parent.toolkit_widget
        except AttributeError:
            toolkit_parent = None

        # The following blocks perform roughly the same setup process
        # as BaseComponent.setup(), except that we don't need to perform
        # the setup for this Include instance (since it's already setup).
        # Also, since we don't need to recurse into any children (an
        # Include can't have children), there is no need to break these
        # blocks out into separate methods.

        # Need to explicitly assign the parent to the components 
        # since they were not added via the add_subcomponent method.
        for child in cmpnts:
            child.parent = self
        
        for child in cmpnts:
            child._setup_create_widgets(toolkit_parent)
            
        for child in cmpnts:
            child._setup_init_widgets()

        for child in cmpnts:
            child._setup_eval_expressions()

        for child in cmpnts:
            child._setup_bind_widgets()
                
        for child in cmpnts:
            child._setup_listeners()

        for child in cmpnts:
            child._setup_init_visibility()

        for child in cmpnts:
            child._setup_init_layout()

        for child in cmpnts:
            child._setup_finalize()

        for child in cmpnts:
            child._setup_set_initialized()

        self._components_initialized = True

    #--------------------------------------------------------------------------
    # Parent Class Overrides 
    #--------------------------------------------------------------------------
    def add_subcomponent(self, component):
        """ An overriden parent class method which prevents subcomponents
        from being declared for an Include instance.

        """
        msg = ("Cannot add subcomponents to an Include. Assign a component "
               "or a list components to the 'components' attribute instead.")
        raise ValueError(msg)

    def get_actual(self):
        """ A reimplemented parent class method to include the dynamic
        children of this Include in our parent's list of children.

        """
        if self._components_initialized:
            res = sum([c.get_actual() for c in self.components], [])
        else:
            res = []
        return res

    def destroy(self):
        """ A re-implemented parent class method which destroys all of
        the underlying dynamic children.

        """
        super(Include, self).destroy()
        for item in self.components:
            item.destroy()

    #--------------------------------------------------------------------------
    # Change Handlers 
    #--------------------------------------------------------------------------
    def _components_changed(self, name, old, new):
        """ Reacts to changes in the dynamic components and sets up the 
        new children, making sure the old ones are destroyed and that 
        the '_actual_updated' event gets fired.

        """
        # The first time a cached property is set, the notification
        # handler will be sent None as the old value even if the 
        # property getter points to something that has a value. In 
        # all other cases, it works as expected. We guard against
        # that condition as well a making sure the object is fully
        # initialized before destroying any of the old children.
        if self.initialized and old is not None:
            def closure():
                for item in old:
                    item.destroy()
                self._setup_components()
                self._actual_updated()
            self.request_relayout_task(closure)
            
    # This notifier is hooked up in the '_handle_initialized' method 
    # due to issues surrounding trait_setq contexts.
    def _on_components_actual_updated(self):
        """ Handles a '_actual_updated' event being fired by one 
        the dynamic components. The event is proxied up the tree by
        firing the same event on this instance. This allows a nested
        Include to update its contents independent of the Include in
        which it is nested.

        """        
        self._actual_updated()

