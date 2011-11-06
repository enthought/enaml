#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------

from abc import abstractmethod

from traits.api import Instance, Range, Int, Constant, Property, on_trait_change

from .container import Container, AbstractTkContainer
from .layout.layout_manager import NullLayoutManager


class AbstractTkStacked(AbstractTkContainer):
    """ The abstract toolkit Container interface.

    A toolkit stacked container is responsible for handling changes on a shell
    Stacked and proxying those changes to and from its internal toolkit widget.

    """

    @abstractmethod
    def shell_index_changed(self, index):
        raise NotImplementedError

    @abstractmethod
    def shell_children_changed(self, children):
        raise NotImplementedError

    @abstractmethod
    def shell_children_items_changed(self, event):
        raise NotImplementedError


class Stacked(Container):
    """ A Container that displays just one of its children at a time.

    """

    #: The index of the currently displayed child.
    index = Range(low='_zero', high='_nchildren', value=0)

    #: An object that manages the layout of this component and its 
    #: direct children. In this case, it does nothing.
    layout = Instance(NullLayoutManager, ())

    #: Just a constant 0 for the index Range trait to use as a lower bound.
    _zero = Constant(0)

    #: The upper bound for the index Range trait. Just the length of the
    #: `children` list.
    _nchildren = Property(Int, depends_on=['children', 'children_items'])

    #: How strongly a component hugs it's contents' width.
    #: Stacked containers ignore the width hug by default, so they expand freely
    #: in width.
    hug_width = 'ignore'

    #: How strongly a component hugs it's contents' height.
    #: Stacked containers ignore the height hug by default, so they expand freely
    #: in height.
    hug_height = 'ignore'

    def initialize_layout(self):
        """ Initialize the layout of the children.

        """
        for child in self.children:
            if hasattr(child, 'initialize_layout'):
                child.initialize_layout()

    @on_trait_change('children:size_hint_updated, children:hug_width, children:hug_height, children:resist_clip_width, children:resist_clip_height')
    def handle_size_hint_changed(self, child, name, old, new):
        """ Pass up the size hint changed notification.

        """
        self.size_hint_updated = True

    def _get__nchildren(self):
        """ Property getter for `_nchildren`.

        """
        return len(self.children)
