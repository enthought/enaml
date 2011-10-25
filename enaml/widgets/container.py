#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance, List, Either

from .component import Component, AbstractTkComponent
from .control import Control
from .layout_item import LayoutItem, AbstractTkLayoutItem

from ..layout.layout_manager import AbstractLayoutManager
from ..layout.constraints_layout import ConstraintsLayout


class AbstractTkContainer(AbstractTkComponent, AbstractTkLayoutItem):
    pass


class Container(Component, LayoutItem):
    """ The base container interface. 
    
    Containers are non-visible components that are responsible for 
    laying out and arranging their children.

    """
    layout = Instance(AbstractLayoutManager, factory=ConstraintsLayout)

    #--------------------------------------------------------------------------
    # Overridden parent class traits
    #--------------------------------------------------------------------------
    abstract_widget = Instance(AbstractTkContainer)

    children = List(Either(Instance(Control), Instance('Container')))

    def add_child(self, child):
        # XXX make me dynamic
        self.children.append(child)

    def remove_child(self, child):
        # XXX implement me
        raise NotImplementedError

    def replace_child(self, child, other_child):
        # XXX implement me
        raise NotImplementedError
       
    def swap_children(self, child, other_child):
        # XXX implement me
        raise NotImplementedError

    def initialize_layout(self):
        super(Container, self).initialize_layout()
        self.layout.initialize(self)

    def relayout(self):
        self.layout.layout(self)

    def reconstrain(self):
        self.layout.initialize(self)

    def _layout_changed(self):
        self.reconstrain()
        self.relayout()

