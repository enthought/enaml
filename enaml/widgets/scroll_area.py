#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------

from abc import abstractmethod

from traits.api import Instance, Either, Enum, List, Tuple, Int

from .container import Container, AbstractTkContainer
from .control import Control
from .layout.layout_manager import NullLayoutManager


#: Enum trait describing the scrollbar policies that can be assigned to the
#: horizontal and vertical scrollbars.
ScrollbarPolicy = Enum('as_needed', 'always_on', 'always_off')

class AbstractTkScrollArea(AbstractTkContainer):
    """ The abstract toolkit ScrollArea interface.

    A toolkit stacked container is responsible for handling changes on a shell
    ScrollArea and proxying those changes to and from its internal toolkit widget.

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

    #: The preferred size of the scroll area.
    #: Each component of the tuple can be either None or an integer. If None,
    #: then that component is requested from the child widget's size hint.
    #: By default, the height is fixed to 200 and the width is taken from the
    #: widget. This accounts for the usual case where we want to display a lot
    #: of vertically laid-out information in a confined area.
    preferred_size = Tuple(Either(None, Int, default=None), Either(Int, None, default=200))

    #: An object that manages the layout of this component and its 
    #: direct children. In this case, it does nothing.
    layout = Instance(NullLayoutManager, ())

    #: Do not hug our content.
    hug_width = 'ignore'
    hug_height = 'ignore'

    #: Overridden parent class trait.
    #: Only one child is allowed.
    children = List(Either(Instance(Control), Instance(Container)), maxlen=1)

    def initialize_layout(self):
        """ Initialize the layout of the children.

        """
        for child in self.children:
            if hasattr(child, 'initialize_layout'):
                child.initialize_layout()

    def size_hint(self):
        """ Use the given preferred size when specified and the widget's size
        hint when not.

        """
        width, height = self.preferred_size
        width_hint, height_hint = self.abstract_obj.size_hint()
        if width is None:
            width = width_hint
        if height is None:
            height = height_hint
        return (width, height)

    def _preferred_size_changed(self):
        """ Update parent constraints when we change our preferred size.

        """
        if self.parent is not None:
            self.parent.set_needs_update_constraints(True)
