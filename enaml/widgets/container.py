#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import deque

from traits.api import List, Instance, Bool

from .component import Component, AbstractTkComponent
from .layout.constraints_layout import ConstraintsLayout
from .layout.layout_manager import AbstractLayoutManager

from ..guard import guard


class AbstractTkContainer(AbstractTkComponent):
    """ The abstract toolkit Container interface.

    A toolkit container is responsible for handling changes on a shell
    Container object and proxying those changes to and from its internal 
    toolkit widget.

    """
    pass


c = 1
def print_relayout(obj):
    global c
    print 'relayout', c, obj
    c += 1


class Container(Component):
    """ A Component subclass that provides for laying out its child 
    Components.

    """
    #: An object that manages the layout of this component and its
    #: direct children. The default is constraints based layout.
    layout_manager = Instance(AbstractLayoutManager)
    def _layout_manager_default(self):
        return ConstraintsLayout(self)

    #: A list of user-specified linear constraints defined for this 
    #: container.
    constraints = List

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkContainer)

    #: A private boolean flag indictating whether a relayout is pending.
    _relayout_pending = Bool(False)

    #: A private boolean flag indicating whether a rearrange is pending.
    _rearrange_pending = Bool(False)

    #: A private queue of callables pending a relayout.
    _relayout_queue = Instance(deque, ())

    #: A private queue callables pending a rearrange.
    _rearrange_queue = Instance(deque, ())

    #: A private boolean flag indicating whether processing of the
    #: relayout queue is occuring.
    _relayout_queue_processing = Bool(False)

    #: A private boolean flag indicating whether processing of the
    #: rearrange queue is occuring.
    _rearrange_queue_processing = Bool(False)

    #--------------------------------------------------------------------------
    # Layout Handling
    #--------------------------------------------------------------------------
    def initialize_layout(self):
        """ Initialize the layout for the first time. Called at the end
        of the setup process.

        """
        if self.layout_manager is not None:
            self.layout_manager.initialize()
        # These handlers are bound dynamically here instead of via
        # decorators since the children are initially computed quietly.
        # Binding the handlers here ensures the listeners are properly
        # initialized with their dependencies.
        self.on_trait_change(self._on_child_visibility, 'children:visible')
        self.on_trait_change(self._on_constraints_changed, 'constraints[]')
        self.on_trait_change(
            self._on_size_hint_changed, 
            'children:size_hint_updated, children:hug_width, '
            'children:hug_height, children:resist_clip_width, '
            'children:resist_clip_height'
        )

    def relayout(self):
        """ Reimplemented parent class method which triggers an update
        of the constraints and a layout refresh. This is called whenever
        the children of the component should have their layout refreshed. 
        The constraints update and relayout occur immediately and are 
        completed before the method returns.

        """
        layout_mgr = self.layout_manager
        if layout_mgr is None:
            super(Container, self).relayout()
        else:
            # Protect against relayout recursion.
            if not guard.guarded(self, 'relayout'):
                with guard(self, 'relayout'):
                    print_relayout(self)
                    layout_mgr.update_constraints()
                    layout_mgr.layout()
                    self._relayout_pending = False

    def relayout_later(self):
        """ Reimplemented parent class method which triggers an update
        of the constraints and a layout refresh at some point in the 
        future.

        """
        layout_mgr = self.layout_manager
        if layout_mgr is None:
            super(Container, self).relayout_later()
        else:
            # Squash multiple calls to relayout_later if there is 
            # already a relayout pending.
            if not self._relayout_pending:
                self._relayout_pending = True
                print 'relayout later'
                self.toolkit.invoke_later(self.relayout)
    
    def rearrange(self):
        """ Reimplemented parent class method which triggers a rearrange
        of the children.

        """
        layout_mgr = self.layout_manager
        if layout_mgr is None:
            super(Container, self).rearrange()
        else:
            # Protect against rearrange recursion.
            if not guard.guarded(self, 'rearrange'):
                with guard(self, 'rearrange'):
                    layout_mgr.layout()
                    self._rearrange_pending = False

    def rearrange_later(self):
        """ Reimplemented parent class method which triggers a rearrange
        of the children at some point in the future.

        """
        layout_mgr = self.layout_manager
        if layout_mgr is None:
            super(Container, self).rearrange_later()
        else:
            # Squash multiple calls to rearrange_later if there is
            # already a rearrange pending.
            if not self._rearrange_pending:
                print 'rearrange later'
                self._rearrange_pending = True
                self.toolkit.invoke_later(self.rearrange)

    def relayout_enqueue(self, callable):
        """ Reimplemented parent class method which triggers a rearrange
        after adding the callable to the queue.

        """
        if self.layout_manager is None:
            super(Container, self).relayout_enqueue(callable)
        else:
            print 'enque', self
            self._relayout_queue.append(callable)
            # Measuring the size of the queue is not a reliable indicator
            # of when we need to invoke the method to purge the queue.
            # So, we use a flag instead.
            if not self._relayout_queue_processing:
                self._relayout_queue_processing = True
                print 'empty layoutq later', self
                self.toolkit.invoke_later(self._empty_relayout_queue)

    def rearrange_enqueue(self, callable):
        """ Reimplemented parent class method which trigger a rearrange
        after after adding the callable to the queue.

        """
        if self.layout_manager is None:
            super(Container, self).rearrange_enqueue(callable)
        else:
            self._rearrange_queue.append(callable)
            # Measuring the size of the queue is not a reliable indicator
            # of when we need to invoke the method to purge the queue.
            # So, we use a flag instead.
            if not self._rearrange_queue_processing:
                self._rearrange_queue_processing = True
                self.toolkit.invoke_later(self._empty_rearrange_queue)
        
    def _empty_relayout_queue(self):
        """ An internal callback which empties the relayout queue from
        within a freeze context.

        """
        with self.freeze():
            queue = self._relayout_queue
            while queue:
                queue.popleft()()
            self._relayout_queue_processing = False
            self.relayout()
        
    def _empty_rearrange_queue(self):
        """ An internal callback which empties the rearrange queue from
        within a freeze context.

        """
        with self.freeze():
            queue = self._rearrange_queue
            while queue:
                queue.popleft()()
            self._rearrange_queue_processing = False
            self.rearrange()
        
    #--------------------------------------------------------------------------
    # Default Constraint Generation
    #--------------------------------------------------------------------------
    def default_user_constraints(self):
        """ Constraints to use if the constraints trait is an empty list.
        
        Default behaviour is to put the children into a vertical layout.
        Subclasses of Container which implement container_constraints will
        probably want to override this (possibly to return an empty list).

        """
        from .layout.layout_helpers import vbox
        return [vbox(*self.children)]

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
        """ A change handler for triggering a relayout when a child of
        the container toggles its visibility.

        """
        # When visibility changes, we need to ensure a relayout takes
        # place from within a freeze context. We can do this by adding
        # an empty callable to the queue. This ensures that we don't 
        # relayout more than is necessary.
        self.relayout_enqueue(lambda: None)

    def _on_size_hint_changed(self, child, name, old, new):
        """ A change handler for updaing the layout when the size hint
        of any of the container's children have changed.

        """
        if self.layout_manager is None:
            # Our layout is managed by an ancestor, so pass up 
            # the notification.
            #
            # XXX this is fragile since it's assuming the parent
            # will be a Container.
            self.parent._on_size_hint_changed(child, name, old, new)
        else:
            # We want to update the size constraints of the layout 
            # manager before the relayout takes place. We can do this
            # by placing a callable on the rearrange queue. This also
            # ensures that we do not rearrange more than is necessary.
            # Note, the updating the size constraints is a special cased
            # operation of the layout manager since it it's likely to
            # happen more often than a full relayout. Thus it's more
            # efficient than performing a full relayout.
            def size_hint_closure():
                self.layout_manager.update_size_cns(child)
            self.rearrange_enqueue(size_hint_closure)

    def _on_constraints_changed(self):
        """ A change handler that triggers a relayout when the list of 
        constraints for the container change.

        """
        # When constraints change, we need to ensure a relayout takes
        # place from within a freeze context. We can do this by adding
        # an empty callable to the queue. This ensures that we don't 
        # relayout more than is necessary.
        self.relayout_enqueue(lambda: None)

