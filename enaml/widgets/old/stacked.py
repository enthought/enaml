#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance, Range, Int, Constant, Property, on_trait_change, List

from .container import Container, AbstractTkContainer
from .layout.layout_manager import NullLayoutManager


_SIZE_HINT_DEPS = ('children:size_hint_updated, children:hug_width, '
                   'children:hug_height, children:resist_clip_width, '
                   'children:resist_clip_height, index')


class AbstractTkStacked(AbstractTkContainer):
    """ The abstract toolkit Container interface.

    A toolkit stacked container is responsible for handling changes on 
    a shell Stacked and proxying those changes to and from its internal 
    toolkit widget.

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

    #: How strongly a component hugs it's contents' width. A Stacked
    #: container ignores its width hug by default, so it expands freely
    #: in width.
    hug_width = 'ignore'

    #: How strongly a component hugs it's contents' height. A Stacked
    #: container ignores its height hug by default, so it expands freely
    #: in height.
    hug_height = 'ignore'

    def initialize_layout(self):
        """ Initialize the layout of the children. This is overridden
        from the parent class since Stacked container does not use
        a constraints layout manager. That is, a Stacked container is
        a boundary which constraints may not cross.

        """
        for child in self.children:
            if hasattr(child, 'initialize_layout'):
                child.initialize_layout()

    @on_trait_change(_SIZE_HINT_DEPS)
    def handle_size_hint_changed(self, child, name, old, new):
        """ Pass up the size hint changed notification to the parent
        so that a window resize can take place if necessary.

        """
        self.size_hint_updated = True

    def _get__nchildren(self):
        """ Property getter for `_nchildren`.

        """
        return len(self.children)

