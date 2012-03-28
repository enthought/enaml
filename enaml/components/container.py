#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (
    List, Instance, Property, cached_property, Bool, WeakRef
)

from .constraints_widget import (
    ConstraintsWidget, AbstractTkConstraintsWidget,
)
from .layout_task_handler import LayoutTaskHandler

from ..layout.constrainable import PaddingConstraints, Constrainable
from ..layout.constraints_layout import ConstraintsLayout
from ..layout.layout_helpers import expand_constraints
from ..layout.geometry import Size, Box
    

class AbstractTkContainer(AbstractTkConstraintsWidget):
    """ The abstract toolkit Container interface.

    """
    pass


class Container(LayoutTaskHandler, PaddingConstraints, ConstraintsWidget):
    """ A Component subclass that provides functionality for laying out 
    constrainable children according to their system of constraints.

    """
    #: A read-only cached property which returns the constraints layout
    #: manager for this container, or None if the layout is being managed
    #: by a parent container.
    layout_manager = Property(
        Instance(ConstraintsLayout), depends_on='owns_layout',
    )

    #: The list of children that can participate in constraints based
    #: layout. This list is composed of components in the list of 
    #: children that are instances of Constrainable.
    constraints_children = Property(
        List(Instance(Constrainable)), depends_on='children',
    )

    #: A read-only property which returns True if this container owns
    #: its layout and is responsible for setting the geometry of its
    #: children, or False if that responsibility has been transferred
    #: to another component in the hierarchy.
    owns_layout = Property(Bool, depends_on='_layout_owner')

    #: A container has a default padding of 10 on all sides.
    padding = Box(10, 10, 10, 10)
    
    #: A private trait which stores a weak reference to the owner of 
    #: the layout for this container, or None if this container owns 
    #: its layout.
    _layout_owner = WeakRef(allow_none=True)

    #: A private cached property which computes the size hint whenever 
    #: the size_hint_updated event is fired.
    _size_hint = Property(Instance(Size), depends_on='size_hint_updated')

    #: Overridden parent class trait.
    abstract_obj = Instance(AbstractTkContainer)

    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_constraints_children(self):
        """ Cached property getter for the 'constraints_children' 
        attribute. This getter returns the sublist of children that are 
        instances of ConstraintsWidget.

        """
        flt = lambda child: isinstance(child, Constrainable)
        return filter(flt, self.children)
    
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
    def _constraints_children_changed(self):
        """ A handler which requests a relayout when the constraints
        children change, provided that the container is initialized.

        """
        if self.initialized:
            self.request_relayout()

    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def _setup_init_layout(self):
        """ A reimplemented parent class setup method that performs any
        layout initialization necessary for the component. The layout is
        initialized from the bottom up.

        """
        super(Container, self)._setup_init_layout()
        self.initialize_layout()

    #--------------------------------------------------------------------------
    # Layout Handling
    #--------------------------------------------------------------------------
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
            self._layout_owner.request_relayout_task(callback, *args, **kwargs)
            
    def request_refresh_task(self, callback, *args, **kwargs):
        """ A reimplemented parent class method which forwards the call
        to the layout owner if necessary.

        """
        if self.owns_layout:
            sup = super(Container, self)
            sup.request_refresh_task(callback, *args, **kwargs)
        else:
            self._layout_owner.request_refresh_task(callback, *args, **kwargs)
        
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
        # recomputing everything from scratch, but that will require
        # tracking the created constraints so for now we just punt.
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
        # this point, we just have to do a refresh.
        width = self.width
        height = self.height
        size = self.size()
        self.layout_manager.layout(self.apply_layout, width, height, size)

    def apply_layout(self):
        """ The callback invoked by the layout manager when there are
        new layout values available. This traverses the constraints 
        children for which this container has layout ownership and 
        applies the geometry updates.

        """
        stack = [((0, 0), self.constraints_children)]
        pop = stack.pop
        push = stack.append
        while stack:
            offset, children = pop()
            for child in children:
                new_offset = child.update_layout_geometry(*offset)
                if isinstance(child, Container):
                    if child._layout_owner is self:
                        push((new_offset, child.constraints_children))

    #--------------------------------------------------------------------------
    # Constraints Computation
    #--------------------------------------------------------------------------
    def compute_constraints(self):
        """ Descends the tree for all containers and children for which
        this container can manage layout, and aggregates all of their
        constraints into a single list.

        """
        expand = expand_constraints

        cns = []
        cns_extend = cns.extend

        # We don't care about the size hint constraints for a container
        # which manages a layout because the actual size is the input
        # to the solver.
        cns_extend(expand(self, self.hard_constraints()))
        cns_extend(expand(self, self.padding_constraints()))
        cns_extend(expand(self, self.user_constraints()))
        cns_extend(expand(self, self.component_constraints()))

        stack = list(self.constraints_children)
        stack_pop = stack.pop
        stack_extend = stack.extend
        while stack:
            child = stack_pop()
            if isinstance(child, Container):
                # When we take over layout ownership of a container we
                # don't care about its size hint constraints since we
                # deal with its children directly.
                if child.transfer_layout_ownership(self):
                    cns_extend(expand(child, child.hard_constraints()))
                    cns_extend(expand(child, child.padding_constraints()))
                    cns_extend(expand(child, child.user_constraints()))
                    cns_extend(expand(child, child.component_constraints()))
                    stack_extend(child.constraints_children)
                else:
                    # If we aren't taking over layout ownership, then we
                    # don't care about any of the container's internal 
                    # constraints.
                    cns_extend(expand(child, child.hard_constraints()))
                    cns_extend(expand(child, child.size_hint_constraints()))
            else:
                cns_extend(expand(child, child.hard_constraints()))
                cns_extend(expand(child, child.size_hint_constraints()))
                cns_extend(expand(child, child.user_constraints()))
                cns_extend(expand(child, child.component_constraints()))
                if isinstance(child, PaddingConstraints):
                    cns_extend(expand(child, child.padding_constraints()))
                    
        return cns

    def default_user_constraints(self):
        """ Constraints to use if the constraints trait is an empty list.
        The default container behavior is to put the layout children into
        a vertical box layout.

        """
        from ..layout.layout_helpers import vbox
        return [vbox(*self.constraints_children)]

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def size_hint(self):
        """ Overridden parent class method to return the size hint of 
        the container from the layout manager. If the container does not
        own its layout, or if the layout has not been initialized, then
        this method will return (-1, -1). This method does not rely on 
        the size hint computation of the underlying toolkit widget. Thus,
        the underlying widget may call back into this method as needed
        to get a size hint from the layout manager.

        """
        # Since this may be called very often by user code, especially 
        # if the toolkit widget is using it as a replacement for its
        # internal size hint computation, we must cache the value or
        # it will be too expensive to use under heavy resize loads.
        # This returns the value from the cached property which is 
        # updated whenver the size_hint_updated event is fired.
        return self._size_hint

    #--------------------------------------------------------------------------
    # Auxiliary Methods
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
            res = Size(int(round(w)), int(round(h)))
        else:
            res = Size(-1, -1)
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
            res = Size(int(round(w)), int(round(h)))
        else:
            res = Size(-1, -1)
        return res

