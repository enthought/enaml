#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import List, Instance, Either, Bool, on_trait_change

from .component import Component, AbstractTkComponent
from .control import Control
from .layout.constraints_layout import ConstraintsLayout
from .layout.layout_manager import AbstractLayoutManager


_SIZE_HINT_DEPS = ('children:size_hint_updated, children:hug_width, '
                   'children:hug_height, children:resist_clip_width, '
                   'children:resist_clip_height')


_CONSTRAINT_DEPS = 'constraints, constraints_items'


class AbstractTkContainer(AbstractTkComponent):
    """ The abstract toolkit Container interface.

    A toolkit container is responsible for handling changes on a shell
    Container object and proxying those changes to and from its internal 
    toolkit widget.

    """
    pass


class Container(Component):
    """ A Component subclass that provides for laying out child 
    Components.

    """
    #: An object that manages the layout of this component and its
    #: direct children. The default is simple constraints based
    layout = Instance(AbstractLayoutManager)

    #: A list of user-specified linear constraints defined for this 
    #: container.
    constraints = List()

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkContainer)

    #: Overridden parent class trait
    children = List(Either(Instance(Control), Instance('Container')))
    
    #: A private boolean indicating if the contraints have changed
    #: and need to be updated on the next pass.
    _needs_update_constraints = Bool(True)

    #: A private boolean indicating if the component needs to relayout
    #: its children
    _needs_layout = Bool(True)

    def _layout_default(self):
        """ Default value for the layout manager.

        """
        return ConstraintsLayout(self)

    def setup(self):
        """ Run the setup process for the ui tree. This is overridden 
        from the parent class to add initialize_layout to the setup.

        """
        # XXX make layout setup a completely separate pass
        # probably handled by the view object.
        super(Container, self).setup()
        self.initialize_layout()

    def initialize_layout(self):
        """ Initialize the layout for the first time.

        """
        if self.layout is not None:
            self.layout.initialize()
    
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

    def update_constraints_if_needed(self):
        """ Update the constraints of this component if necessary. This
        is typically the case when a constraint has been changed.

        """
        if self._needs_update_constraints:
            self.toolkit.invoke_later(self.update_constraints)

    def set_needs_update_constraints(self, needs=True):
        """ Indicate that the constraints for this component should be
        updated some time later.

        """
        if self.layout is None:
            # Our layout is being managed by an ancestor.
            if needs:
                self.parent.set_needs_update_constraints(needs)
        else:
            self._needs_update_constraints = needs
            if needs:
                self.toolkit.invoke_later(self.update_constraints)

    def update_constraints(self):
        """ Update the constraints for this component.

        """
        if self.layout is not None:
            self.layout.update_constraints()
            self.set_needs_layout(True)
        self._needs_update_constraints = False

    def layout_if_needed(self):
        """ Refreshes the layout of this component if necessary. This
        will typically be needed if this component has been resized or
        the sizes of any of its children have been changed.

        """
        if self._needs_layout:
            self.toolkit.invoke_later(self.do_layout)

    def set_needs_layout(self, needs=True):
        """ Indicate that the layout should be refreshed some time later.

        """
        if self.layout is None:
            # Our layout is being managed by an ancestor.
            self.parent.set_needs_layout(needs)
        else:
            old = self._needs_layout
            self._needs_layout = needs
            if not old and needs:
                # Only invoke the do_layout() once, when _needs_layout 
                # changes from False to True, but not when it was already 
                # True. This makes sure that we only update the layout once 
                # even if we set multiple traits that request a new layout.
                self.toolkit.invoke_later(self.do_layout)

    def do_layout(self):
        """ Updates the layout of this component.

        """
        if self.layout is not None:
            self.layout.layout()
        self._needs_layout = False

    @on_trait_change(_SIZE_HINT_DEPS)
    def handle_size_hint_changed(self, child, name, old, new):
        """ A change handler for updaing the layout when the size hint
        of any of the container's children have changed.

        """
        if self.layout is None:
            # Our layout is managed by an ancestor, so pass up 
            # the notification.
            self.parent.handle_size_hint_changed(child, name, old, new)
        else:
            # Update the constraints in the solver immediately since
            # there may be more than one widget during a pass that
            # will the size hint updated, and multiple calls to 
            # set_needs_layout get collapsed to a single call. If we
            # were to update the size hint cns via invoke_later, some
            # of the updates may occur after the layout pass has already
            # taken place.
            self.layout.update_size_cns(child)
            self.set_needs_layout()

    @on_trait_change(_CONSTRAINT_DEPS)
    def handle_constraints_changed(self):
        """ A handler for updating the layout when the constraints of the
        container change.

        """
        if self.layout is None or self.layout._initialized:
            self.set_needs_update_constraints()
            self.set_needs_layout()

    @on_trait_change('children:visible')
    def handle_visible_changed(self, child, name, old, new):
        if self.layout is None or self.layout._initialized:
            self.set_needs_update_constraints()
            self.set_needs_layout()

