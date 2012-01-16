#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import List, Instance

from .layout_component import LayoutComponent, AbstractTkLayoutComponent
from .layout.constraints_layout import ConstraintsLayout
from .layout.layout_manager import AbstractLayoutManager
from .layout_task_handler import LayoutTaskHandler


class AbstractTkContainer(AbstractTkLayoutComponent):
    """ The abstract toolkit Container interface.

    A toolkit container is responsible for handling changes on a shell
    Container object and proxying those changes to and from its internal 
    toolkit widget.

    """
    pass


class Container(LayoutTaskHandler, LayoutComponent):
    """ A Component subclass that provides for laying out its layout
    child Components.

    """
    #: An object that manages the layout of this component and its
    #: layout children. The default is constraints based layout.
    layout_manager = Instance(AbstractLayoutManager)
    def _layout_manager_default(self):
        return ConstraintsLayout(self)

    #: A list of user-specified linear constraints defined for this 
    #: container.
    constraints = List

    #: Overridden parent class trait.
    abstract_obj = Instance(AbstractTkContainer)

    #--------------------------------------------------------------------------
    # Layout Handling
    #--------------------------------------------------------------------------
    def initialize_layout(self):
        """ A reimplemented parent class method that initializes the 
        layout manager for the first time, and binds the relevant
        layout change handlers.

        """
        # The layout manager will be destructively set to None by any
        # parent Containers since they will take over layout management
        # of their layout children.
        if self.layout_manager is not None:
            self.layout_manager.initialize()
        # These handlers are bound dynamically here instead of via
        # decorators since the layout children are initially computed 
        # quietly. Binding the handlers here ensures the listeners are 
        # properly initialized with their dependencies.
        self.on_trait_change(self._on_child_visibility, 'layout_children:visible')
        self.on_trait_change(self._on_constraints_changed, 'constraints[]')
        self.on_trait_change(
            self._on_size_hint_changed, 
            'layout_children:size_hint_updated, layout_children:hug_width, '
            'layout_children:hug_height, layout_children:resist_clip_width, '
            'layout_children:resist_clip_height'
        )

    def relayout(self):
        """ A reimplemented parent class method which proxies the call
        to relayout up the heierarchy if necessary. 

        """
        # If our layout manager is None, we have a parent container
        # that is managing layout for us. In that case, we continue
        # to proxy the call up the heierarchy.
        if self.layout_manager is None:
            self.parent.relayout()
        else:
            super(Container, self).relayout()
    
    def refresh(self):
        """ A reimplemented parent class method which proxies the call
        to refresh up the heierarchy if necessary. 

        """
        # If our layout manager is None, we have a parent container
        # that is managing layout for us. In that case, we continue
        # to proxy the call up the heierarchy.
        if self.layout_manager is None:
            self.parent.refresh()
        else:
            super(Container, self).refresh()

    def request_relayout(self):
        """ A reimplemented parent class method which proxies the call
        to request_relayout up the heierarchy if necessary. 

        """
        # If our layout manager is None, we have a parent container
        # that is managing layout for us. In that case, we continue
        # to proxy the call up the heierarchy.
        if self.layout_manager is None:
            self.parent.request_relayout()
        else:
            super(Container, self).request_relayout()

    def request_refresh(self):
        """ A reimplemented parent class method which proxies the call
        to request_refresh up the heierarchy if necessary. 

        """
        # If our layout manager is None, we have a parent container
        # that is managing layout for us. In that case, we continue
        # to proxy the call up the heierarchy.
        if self.layout_manager is None:
            self.parent.request_refresh()
        else:
            super(Container, self).request_refresh()

    def request_relayout_task(self, callback, *args, **kwargs):
        """ A reimplemented parent class method which proxies the call
        to request_relayout_task up the heierarchy if necessary. 

        """
        # If our layout manager is None, we have a parent container
        # that is managing layout for us. In that case, we continue
        # to proxy the call up the heierarchy.
        if self.layout_manager is None:
            self.parent.request_relayout_task(callback, *args, **kwargs)
        else:
            sup = super(Container, self)
            sup.request_relayout_task(callback, *args, **kwargs)
            
    def request_refresh_task(self, callback, *args, **kwargs):
        """ A reimplemented parent class method which proxies the call
        to request_refresh_task up the heierarchy if necessary. 

        """
        # If our layout manager is None, we have a parent container
        # that is managing layout for us. In that case, we continue
        # to proxy the call up the heierarchy.
        if self.layout_manager is None:
            self.parent.request_refresh_task(callback, *args, **kwargs)
        else:
            sup = super(Container, self)
            sup.request_refresh_task(callback, *args, **kwargs)
        
    #--------------------------------------------------------------------------
    # Layout Implementation Handlers
    #--------------------------------------------------------------------------
    def do_relayout(self):
        """ A reimplemented LayoutTaskHandler handler method which will
        actually perform the layout.

        """
        # At this point, we know that our layout manager is not None
        # and is the proper manager to do the layout, since the layout
        # requests are proxied up the tree until the component with 
        # the active manager is found.
        layout_mgr = self.layout_manager
        layout_mgr.update_constraints()
        layout_mgr.layout()
    
    def do_refresh(self):
        """ A reimplemented LayoutTaskHandler handler method which will
        actually perform the refresh.

        """
        # At this point, we know that our layout manager is not None
        # and is the proper manager to do the layout, since the layout
        # requests are proxied up the tree until the component with 
        # the active manager is found.
        layout_mgr = self.layout_manager
        layout_mgr.layout()
    
    #--------------------------------------------------------------------------
    # Default Constraint Generation
    #--------------------------------------------------------------------------
    def default_user_constraints(self):
        """ Constraints to use if the constraints trait is an empty list.
        
        Default behaviour is to put the layout children into a vertical 
        layout. Subclasses which implement container_constraints will
        probably want to override this (possibly to return an empty list).

        """
        from .layout.layout_helpers import vbox
        return [vbox(*self.layout_children)]

    def container_constraints(self):
        """ A set of constraints that should always be applied to this
        type of container. This should be implemented by subclasses
        such as Form to set up their standard constraints.

        """
        return []

    #--------------------------------------------------------------------------
    # Change Handlers 
    #--------------------------------------------------------------------------
    def _on_child_visibility(self):
        """ A change handler for triggering a relayout when a layout 
        child of the container toggles its visibility.

        """
        self.request_relayout()

    def _on_size_hint_changed(self, child, name, old, new):
        """ A change handler for updaing the layout when the size hint
        of any of the container's layout children have changed.

        """
        layout_mgr = self.layout_manager
        if layout_mgr is None:
            # Our layout is managed by an ancestor, so pass up 
            # the notification.
            #
            # XXX this is fragile since it's assuming the parent
            # will be a Container.
            self.parent._on_size_hint_changed(child, name, old, new)
        else:
            # We want to update the size constraints of the layout 
            # manager before the refresh takes place. Note, the updating
            # the size constraints is a special cased operation of the 
            # layout manager since it it's likely to happen more often 
            # than a full relayout. Thus it's more efficient than 
            # performing a full relayout.
            self.request_refresh_task(layout_mgr.update_size_cns, child)

    def _on_constraints_changed(self):
        """ A change handler that triggers a relayout when the list of 
        constraints for the container change.

        """
        self.request_relayout()

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def size_hint(self):
        """ Overridden parent class method to return the size hint of 
        the container as the computed minimum size.

        """
        # XXX we can probably do better than this. Maybe have the 
        # layout manager compute a preferred size, or some such notion
        return self.get_min_size()

    #--------------------------------------------------------------------------
    # Auxiliary Methods
    #--------------------------------------------------------------------------
    def get_min_size(self):
        """ Calculates the minimum size of the container which would 
        allow all constraints to be satisfied. If this container's
        layout is being managed by a parent, then this method will
        return (-1, -1).

        """
        layout_mgr = self.layout_manager
        if layout_mgr is None:
            res = (-1, -1)
        else:
            w, h = layout_mgr.get_min_size()
            res = (int(round(w)), int(round(h)))
        return res

    def get_max_size(self):
        """ Calculates the maximum size of the container which would 
        allow all constraints to be satisfied. If this container's
        layout is being managed by a parent, then this method will
        return (-1, -1).

        """
        layout_mgr = self.layout_manager
        if layout_mgr is None:
            res = (-1, -1)
        else:
            w, h = layout_mgr.get_max_size()
            res = (int(round(w)), int(round(h)))
        return res

