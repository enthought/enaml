#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from traits.api import List, Instance, Either, Bool, on_trait_change

from .component import Component, AbstractTkComponent
from .control import Control
from .layout.constraints_layout import ConstraintsLayout
from .layout.layout_manager import AbstractLayoutManager
from .layout.symbolics import BaseConstraint


class AbstractTkContainer(AbstractTkComponent):
    """ The abstract toolkit Container interface.

    A toolkit container is responsible for handling changes on a shell 
    Container and proxying those changes to and from its internal toolkit
    widget.

    """


class Container(Component):
    """ A Component subclass that provides for laying out child Components.

    """
    #: A private boolean indicating if the contraints have changed
    #: and need to be updated on the next pass.
    _needs_update_constraints = Bool(True)

    #: A private boolean indicating if the component needs to relayout
    #: its children
    _needs_layout = Bool(True)

    #: An object that manages the layout of this component and its 
    #: direct children. The default is simple constraints based
    layout = Instance(AbstractLayoutManager)

    #: A list of user-specified linear constraints defined for this container.
    constraints = List(Instance(BaseConstraint))

    #: A list of default linear constraints defined by this container.
    #: This is usually only set by specialized subclasses of Container to
    #: conveniently lay out widgets in a particular manner.
    default_constraints = List(Instance(BaseConstraint))

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkContainer)

    #: Overridden parent class trait
    children = List(Either(Instance(Control), Instance('Container')))

    def _layout_default(self):
        """ Default value for the layout manager.

        """
        return ConstraintsLayout(self)

    def setup(self):
        """ Run the setup process for the ui tree.

        This is overridden to add the layout set up.

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
        self._needs_update_constraints = needs
        if needs:
            self.toolkit.invoke_later(self.update_constraints)

    def update_constraints(self):
        """ Update the constraints for this component.

        """
        if self.layout is not None:
            self.layout.update_constraints()
        self._needs_update_constraints = False

    def layout_if_needed(self):
        """ Refreshes the layout of this component if necessary. This 
        will typically be needed if this component has been resized or 
        the sizes of any of its children have been changed.

        """
        if self._needs_layout:
            self.toolkit.invoke_later(self.do_layout)

    def set_needs_layout(self, needs=True):
        """ Indicate that the layout should be refreshed some time 
        later.

        """
        self._needs_layout = needs
        if needs:
            self.toolkit.invoke_later(self.do_layout)

    def do_layout(self):
        """ Updates the layout of this component.

        """
        if self.layout is not None:
            self.layout.layout()
        self._needs_layout = False

    @on_trait_change('children:size_hint_updated, children:hug, children:compress')
    def handle_size_hint_changed(self, child, name, old, new):
        self.toolkit.invoke_later(self.layout.update_size_cns, child)
        self.set_needs_layout()

    @on_trait_change('constraints,constraints_items,default_constraints,default_constraints_items')
    def handle_constraints_changed(self):
        if self.layout._initialized:
            self.set_needs_update_constraints()
            self.set_needs_layout()

