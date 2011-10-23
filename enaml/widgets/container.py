#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance, List, Either

from .component import Component, IComponentImpl
from .control import Control

from ..layout.layout_manager import AbstractLayoutManager
from ..layout.constraints_layout import ConstraintsLayout
from ..layout.layout_item import LayoutItem, ILayoutItemImpl


class IContainerImpl(IComponentImpl, ILayoutItemImpl):
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
    toolkit_impl = Instance(IContainerImpl)

    children = List(Either(Instance(Control), Instance('Container')))

    def add_child(self, child):
        child.set_parent(self)
        self.children.append(child)

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

