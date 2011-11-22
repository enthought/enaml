#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance, Range, Int, Constant, Property, on_trait_change, List

from .container import Container, AbstractTkContainer
from .component import Component
from .layout.layout_manager import NullLayoutManager


_SIZE_HINT_DEPS = ('children:size_hint_updated, children:hug_width, '
                   'children:hug_height, children:resist_clip_width, '
                   'children:resist_clip_height')


class AbstractTkSplitter(AbstractTkContainer):
    """ The abstract toolkit Splitter interface.

    A toolkit splitter container is responsible for handling changes on 
    a shell Splitter and proxying those changes to and from its internal 
    toolkit widget.

    """

    @abstractmethod
    def shell_children_changed(self, children):
        raise NotImplementedError

    @abstractmethod
    def shell_children_items_changed(self, event):
        raise NotImplementedError


class Splitter(Container):
    """ A Container that displays just one of its children at a time.

    """
    #: An object that manages the layout of this component and its 
    #: direct children. In this case, it does nothing.
    layout = Instance(NullLayoutManager, ())

    #: How strongly a component hugs it's contents' width. A Splitter
    #: container ignores its width hug by default, so it expands freely
    #: in width.
    hug_width = 'ignore'

    #: How strongly a component hugs it's contents' height. A Splitter
    #: container ignores its height hug by default, so it expands freely
    #: in height.
    hug_height = 'ignore'

    #: Overridden parent class trait.
    children = List(Instance(Component))

    def initialize_layout(self):
        """ Initialize the layout of the children. This is overridden
        from the parent class since the Splitter container does not use
        a constraints layout manager. That is, a Splitter container is
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
