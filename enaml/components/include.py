#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import CList, Instance, Bool, Property, on_trait_change

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

    #: The dynamic components of the Include. This is a component or
    #: list of components which should be included in the children of 
    #: the parent of this Include. Changes made to this list in whole 
    #: or in-place will be reflected as updates in the ui. A single
    #: component will be converted to a single element list.
    components = CList(Instance(BaseComponent))

    #: A private Boolean flag indicating if the dynamic components of 
    #: this Include have been intialized for the first time. This should 
    #: not be manipulated directly by the user.
    _components_initialized = Bool(False)

    #--------------------------------------------------------------------------
    # Property Getters and Setters
    #--------------------------------------------------------------------------    
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
        self._setup_components(self.components)
        self.on_trait_change(
            self._on_components_actual_updated, 'components:_actual_updated',
        )
        self._components_initialized = True
        self._actual_updated()

    def _setup_components(self, components):
        """ Run the setup process for the provided list of components.

        This is a private internal method which is used to run the 
        setup process for a list of new components which should be
        parented by the parent widget of this Include.

        Parameters
        ----------
        components : sequence
            The sequence of BaseComponent instances which should be 
            setup as children of the parent widget for this Include.

        """
        # If we get an empty sequence, don't do any unnecessary work.
        if not components:
            return

        # The dynamic components of an Include are injected into the 
        # parent's children so that they *appear* as if they are 
        # siblings of the Include. To do this, we pass the reference
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
        for child in components:
            child.parent = self
        
        for child in components:
            child._setup_create_widgets(toolkit_parent)
        
        for child in components:
            child._setup_init_widgets()

        for child in components:
            child._setup_eval_expressions()

        for child in components:
            child._setup_bind_widgets()
                
        for child in components:
            child._setup_listeners()

        for child in components:
            child._setup_init_visibility()

        for child in components:
            child._setup_init_layout()

        for child in components:
            child._setup_finalize()

        for child in components:
            child._setup_set_initialized()

    #--------------------------------------------------------------------------
    # Parent Class Overrides 
    #--------------------------------------------------------------------------
    def add_subcomponent(self, component):
        """ An overriden parent class method which prevents subcomponents
        from being declared for an Include instance.

        """
        msg = ("Cannot add subcomponents to an Include. Assign a list of "
               "components to the 'components' attribute instead.")
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
    @on_trait_change('components')
    def _handle_components_changed(self, obj, name, old, new):
        """ A private trait change handler which reacts to changes to 
        the `components` list as a whole.

        """
        self._update_components_diff(set(old), set(new))

    @on_trait_change('components_items')
    def _handle_components_items_changed(self, obj, name, event):
        """ A private trait change handler which reacts to changes in
        the items of the `components` list.

        """
        self._update_components_diff(set(event.removed), set(event.added))

    def _update_components_diff(self, removed, added):
        """ Updates the UI components based on an item diff.

        A private method which will update the components by performing
        diff between the removed and added components. Components no
        longer in use will be destroyed. New components will be setup.

        Parameters
        ----------
        removed : set
            The set of components being removed. This is allowed to 
            overlap with `added` (e.g. a reverse operation).

        added : set
            The set of components being added. This is allowed to 
            overlap with `removed` (e.g. a reverse operation).

        """
        if self.initialized:
            to_destroy = removed - added
            to_setup = added - removed
            def closure():
                for item in to_destroy:
                    item.destroy()
                self._setup_components(to_setup)
                self._actual_updated()
            self.request_relayout_task(closure)

    # This notifier is hooked up in the '_setup_init_layout' method 
    # due to issues surrounding trait_setq contexts.
    def _on_components_actual_updated(self):
        """ Handles a '_actual_updated' event being fired by one 
        the dynamic components. 

        The event is proxied up the tree by firing the same event on 
        this instance. This allows a nested Include to update its 
        contents independent of the Include in which it is nested.

        """        
        self._actual_updated()

