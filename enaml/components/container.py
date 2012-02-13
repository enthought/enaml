#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (
    List, Instance, Property, cached_property, Bool, WeakRef, Tuple, Int,
)

from .layout_component import LayoutComponent, AbstractTkLayoutComponent
from .layout.constraints_layout import ConstraintsLayout
from .layout.layout_helpers import DeferredConstraints
from .layout_task_handler import LayoutTaskHandler


def _expand_constraints(component, constraints):
    """ A private function which expands any DeferredConstraints in
    the provided list. This is generator function which yields the
    flattened stream of constraints.

    Paramters
    ---------
    component : LayoutComponent
        The layout component with which the constraints are associated.
        This will be passed to the .get_constraints_list() method of
        any DeferredConstraint instance.
    
    constraints : list
        The list of constraints, possibly containing instances of 
        DeferredConstraints.
    
    Yields
    ------
    constraints
        The stream of expanded constraints.

    """
    for cn in constraints:
        if isinstance(cn, DeferredConstraints):
            for item in cn.get_constraint_list(component):
                yield item
        else:
            yield cn


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
    #: A read-only cached property which returns the constraints layout
    #: manager for this container, or None in the layout is being managed
    #: by a parent container.
    layout_manager = Property(
        Instance(ConstraintsLayout), depends_on='owns_layout',
    )

    #: A read-only property which returns True if this container owns
    #: its layout and is responsible for setting the geometry of its
    #: children, or False if that responsibility has been transferred
    #: to another component in the hierarchy.
    owns_layout = Property(Bool, depends_on='_layout_owner')

    #: A list of user-specified linear constraints defined for this 
    #: container.
    constraints = List

    #: Overridden parent class trait.
    abstract_obj = Instance(AbstractTkContainer)

    #: A private trait used to indicate that ownership of the layout 
    #: for this container.
    _layout_owner = WeakRef(allow_none=True)

    #: A private cached property which computes the size hint whenever 
    #: the size_hint_updated event is fired.
    _size_hint = Property(Tuple(Int, Int), depends_on='size_hint_updated')

    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_layout_manager(self):
        """ The property getter for the 'layout_manager' attribute.

        """
        if self.owns_layout:
            return ConstraintsLayout()

    def _get_owns_layout(self):
        """ The property getter for the 'owns_layout' attribute.

        """
        return self._layout_owner is None

    @cached_property
    def _get__size_hint(self):
        """ The property getter for the '_size_hint' attribtue.

        """
        # XXX we can probably do better than the min size. Maybe have 
        # the layout manager compute a preferred size, or something
        # similar to a preferred size. But I don't know at the moment
        # what it would actually mean to have a preferred size from 
        # a set of constraints.
        return self.compute_min_size()

    #--------------------------------------------------------------------------
    # Change Handlers 
    #--------------------------------------------------------------------------
    def _on_layout_deps_changed(self):
        """ A change handler for triggering a relayout when any of the
        layout dependencies change. It simply requests a relayout.

        """
        self.request_relayout()

    #--------------------------------------------------------------------------
    # Layout Handling
    #--------------------------------------------------------------------------
    def transfer_layout_ownership(self, owner):
        """ A method which can be called by other components in the
        hierarchy to gain ownership responsibility for the layout 
        of the children of this container. By default, the transfer
        is allowed and is the mechanism which allows constraints to
        cross widget boundaries. Subclasses should reimplement this 
        method if different behavior is desired.

        Parameters
        ----------
        owner : BaseComponent
            The component which has taken ownership responsibility
            for laying out the children of this component. All 
            relayout and refresh requests will be forwarded to this
            component.
        
        Returns
        -------
        results : bool
            True if the transfer was allowed, False otherwise.
        
        """
        self._layout_owner = owner
        return True

    def initialize_layout(self):
        """ A reimplemented parent class method that initializes the 
        layout manager for the first time, and binds the relevant
        layout change handlers.

        """
        # We only need to initialize the manager if we own the layout.
        if self.owns_layout:
            constraints = self.compute_constraints()
            self.layout_manager.initialize(constraints)
            # We fire off a size hint updated event here since, if
            # for some reason, the size hint was computed before 
            # the layout was initialized, the value will be wrong
            # and cached. So we need to clear the cache so that it 
            # will be recomputed by the next consumer that needs it.
            self.size_hint_updated()

        # This relayout dep handler is bound here instead of using a
        # decorator since the layout children are initially computed 
        # quietly. Binding the handler here ensures the listeners are 
        # properly initialized with their dependencies.
        self.on_trait_change(
            self._on_layout_deps_changed, (
                'constraints, '
                'constraints_items, '
                'layout_children, '
                'layout_children:visible, '
                'layout_children:size_hint_updated, '
                'layout_children:hug_width, '
                'layout_children:hug_height, '
                'layout_children:resist_clip_width, '
                'layout_children:resist_clip_height '
            )
        )

    def relayout(self):
        """ A reimplemented parent class method which forwards the call
        to the layout owner if necessary.

        """
        if self.owns_layout:
            super(Container, self).relayout()
        else:
            self._layout_owner.relayout()
            
    def refresh(self):
        """ A reimplemented parent class method which forwards the call
        to the layout owner if necessary.

        """
        if self.owns_layout:
            super(Container, self).refresh()
        else:
            self._layout_owner.refresh()

    def request_relayout(self):
        """ A reimplemented parent class method which forwards the call
        to the layout owner if necessary.

        """
        if self.owns_layout:
            super(Container, self).request_relayout()
        else:
            self._layout_owner.request_relayout()

    def request_refresh(self):
        """ A reimplemented parent class method which forwards the call
        to the layout owner if necessary.

        """
        if self.owns_layout:
            super(Container, self).request_refresh()
        else:
            self._layout_owner.request_refresh()

    def request_relayout_task(self, callback, *args, **kwargs):
        """ A reimplemented parent class method which forwards the call
        to the layout owner if necessary.

        """
        if self.owns_layout:
            sup = super(Container, self)
            sup.request_relayout_task(callback, *args, **kwargs)
        else:
            owner = self._layout_owner
            owner.request_relayout_task(callback, *args, **kwargs)
            
    def request_refresh_task(self, callback, *args, **kwargs):
        """ A reimplemented parent class method which forwards the call
        to the layout owner if necessary.

        """
        if self.owns_layout:
            sup = super(Container, self)
            sup.request_refresh_task(callback, *args, **kwargs)
        else:
            owner = self._layout_owner
            owner.request_refresh_task(callback, *args, **kwargs)
        
    def do_relayout(self):
        """ A reimplemented LayoutTaskHandler handler method which will
        actually perform the layout.

        """
        # At this point, we know that we own the layout since the
        # calls that trigger the call to this method would have 
        # already been forwarded on to the layout owner. So, at
        # this point, we just have to recompute the constraints
        # and do a refresh.

        # TODO There is a big opportunity here to optimize by calling
        # .update_constraints() on the layout manager instead of just
        # recomputing everything from scratch. But, that will require
        # tracking the created constraints.
        self.layout_manager.initialize(self.compute_constraints())
        self.do_refresh()

        # We emit the size hint updated event at this point since
        # we are still inside a freeze context. This means that if
        # our parent is a toplevel window, it can set the new size
        # of the window before leaving the context which helps 
        # eleminate flicker during the resize.
        self.size_hint_updated()

    def do_refresh(self):
        """ A reimplemented LayoutTaskHandler handler method which will
        actually perform the refresh.

        """
        # At this point, we know that we own the layout since the
        # calls that trigger the call to this method would have 
        # already been forwarded on to the layout owner. So, at
        # this point, we just have to recompute the constraints
        # and do a refresh.
        width = self.width
        height = self.height
        size = self.size()
        self.layout_manager.layout(self.apply_layout, width, height, size)

    def apply_layout(self):
        """ The callback invoked by the layout manager when there are
        new layout values available. This traverses the children for
        which this container has layout ownership and applies the 
        geometry updates.

        """
        stack = [((0, 0), self.layout_children)]
        pop = stack.pop
        push = stack.append
        while stack:
            offset, children = pop()
            for child in children:
                new_offset = child.set_solved_geometry(*offset)
                if isinstance(child, Container):
                    if child._layout_owner is self:
                        push((new_offset, child.layout_children))

    #--------------------------------------------------------------------------
    # Constraints Computation
    #--------------------------------------------------------------------------
    def compute_constraints(self):
        """ Computes the constraints for the layout children of this
        container as well as any sub container for which it can usurp
        layout ownership.

        """
        expand = _expand_constraints

        cns = []
        cns_extend = cns.extend
        cns_extend(expand(self, self.hard_constraints()))
        cns_extend(expand(self, self.user_constraints()))
        cns_extend(expand(self, self.container_constraints()))

        stack = list(self.layout_children)
        stack_pop = stack.pop
        stack_extend = stack.extend
        while stack:
            child = stack_pop()
            if isinstance(child, Container):
                # We need to change ownership before asking for the size
                # hint constraints or else a non-initialized container
                # may attempt to run a solver pass to compute the hint
                if child.transfer_layout_ownership(self):
                    cns_extend(expand(child, child.user_constraints()))
                    cns_extend(expand(child, child.container_constraints()))
                    stack_extend(child.layout_children)
            cns_extend(expand(child, child.hard_constraints()))
            cns_extend(expand(child, child.size_hint_constraints()))
        
        return cns

    def user_constraints(self):
        """ Returns the list of constraints specified by the user or the
        list of constraints computed by 'default_user_constraints' if the
        user has not supplied their own list.

        """
        cns = self.constraints
        if not cns:
            cns = self.default_user_constraints()
        return cns

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
    # Overrides
    #--------------------------------------------------------------------------
    def size_hint(self):
        """ Overridden parent class method to return the size hint of 
        the container from the layout manager. If the container does not
        own its layout, or if the layout has not been initialized, then
        this method will return (-1, -1). This method does rely on the
        size hint computation of the underlying toolkit widget. Thus,
        the underlying widget may call back into this method as needed
        to get a size hint from the layout manager.

        """
        # Since this may be very frequently by user code, especially 
        # if the toolkit widget is using it as a replacement for its
        # internal size hint computation, we must cache the value or
        # it will be too expensive to use under heavy resize loads.
        # This returns the value from the cached property which is 
        # updated whenver the size_hint_updated event is fired.
        return self._size_hint

    #--------------------------------------------------------------------------
    # Auxiliary Methods
    #--------------------------------------------------------------------------
    def compute_min_size(self):
        """ Calculates the minimum size of the container which would 
        allow all constraints to be satisfied. If this container does
        not own its layout, or if the layout has not been initialized,
        then this method will return (-1, -1).

        """
        if self.owns_layout and self.layout_manager.initialized:
            width = self.width
            height = self.height
            w, h = self.layout_manager.get_min_size(width, height)
            res = (int(round(w)), int(round(h)))
        else:
            res = (-1, -1)
        return res

    def compute_max_size(self):
        """ Calculates the maximum size of the container which would 
        allow all constraints to be satisfied. If this container does
        not own its layout, or if the layout has not been initialized
        then this method will return (-1, -1).

        """
        if self.owns_layout and self.layout_manager.initialized:
            width = self.width
            height = self.height
            w, h = self.layout_manager.get_max_size(width, height)
            res = (int(round(w)), int(round(h)))
        else:
            res = (-1, -1)
        return res

