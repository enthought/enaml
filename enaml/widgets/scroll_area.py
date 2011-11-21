#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance, Either, Enum, List, Tuple, Int

from .container import Container, AbstractTkContainer
from .control import Control
from .layout.layout_manager import NullLayoutManager


#: Enum trait describing the scrollbar policies that can be assigned to 
#: the horizontal and vertical scrollbars.
ScrollbarPolicy = Enum('as_needed', 'always_on', 'always_off')


class AbstractTkScrollArea(AbstractTkContainer):
    """ The abstract toolkit ScrollArea interface. A toolkit scroll area 
    is responsible for handling changes on a shell ScrollArea and proxying 
    those changes to and from its internal toolkit widget.

    """
    @abstractmethod
    def shell_horizontal_scrollbar_policy_changed(self, policy):
        raise NotImplementedError

    @abstractmethod
    def shell_vertical_scrollbar_policy_changed(self, policy):
        raise NotImplementedError

    @abstractmethod
    def shell_children_changed(self, children):
        raise NotImplementedError

    @abstractmethod
    def shell_children_items_changed(self, event):
        raise NotImplementedError


class ScrollArea(Container):
    """ A Container that displays just one of its children at a time.

    """
    #: The horizontal scroll policy.
    horizontal_scrollbar_policy = ScrollbarPolicy

    #: The vertical scroll policy.
    vertical_scrollbar_policy = ScrollbarPolicy

    #: The preferred (width, height) size of the scroll area. Each item
    #: of the tuple can be either None or an integer. If None, then that 
    #: component is requested from the child widget's size hint. As a
    #: default, the height is fixed to 200 and the width is taken from the
    #: widget. This accounts for the typical use case of display a lot
    #: of vertically laid-out information in a confined area.
    preferred_size = Tuple(Either(None, Int, default=None), 
                           Either(Int, None, default=200))

    #: An object that manages the layout of this component and its 
    #: direct children. In this case, it does nothing.
    layout = Instance(NullLayoutManager, ())

    #: How strongly a component hugs it's contents' width. Scroll
    #: areas do not hug their width and are free to expand.
    hug_width = 'ignore'

    #: How strongly a component hugs it's contents' height. Scroll
    #: areas do not hug their height and are free to expand.
    hug_height = 'ignore'

    #: Overridden parent class trait. Only one child is allowed.
    children = List(Either(Instance(Control), Instance(Container)), maxlen=1)

    def initialize_layout(self):
        """ Initialize the layout of the children. A scroll area does
        not provide or maintain a layout manager, but its children may.
        So, this call is just forwarded on to the children of the scroll
        area.

        """
        for child in self.children:
            if hasattr(child, 'initialize_layout'):
                child.initialize_layout()

    def size_hint(self):
        """ Use the given preferred size when specified and the widget's 
        size hint when not.

        """
        width, height = self.preferred_size
        width_hint, height_hint = self.abstract_obj.size_hint()
        if width is None:
            width = width_hint
        if height is None:
            height = height_hint
        return (width, height)

    def _preferred_size_changed(self):
        """ The change handler for the 'preferred_size' attribute. 
        This emits a proper notification to the layout system to that 
        a relayout can take place.

        """
        self.size_hint_updated = True

