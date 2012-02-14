#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import (
    Property, Instance, Either, Enum, Tuple, Int, cached_property,
    on_trait_change,
)

from .constraints_widget import (
    ConstraintsWidget, AbstractTkConstraintsWidget,
)
from .container import Container
from .layout_task_handler import LayoutTaskHandler
from .widget_component import WidgetComponent

from ..layout.geometry import Size


#: Enum trait describing the scrollbar policies that can be assigned to 
#: the horizontal and vertical scrollbars.
ScrollbarPolicy = Enum('as_needed', 'always_on', 'always_off')


class AbstractTkScrollArea(AbstractTkConstraintsWidget):
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
    def shell_scrolled_component_changed(self, component):
        raise NotImplementedError


class ScrollArea(LayoutTaskHandler, ConstraintsWidget):
    """ A LayoutComponent subclass that displays just a single child in
    a scrollable area.

    """
    #: A read-only property which returns the scrolling component
    #: for the area, or None if one is not defined.
    scrolled_component = Property(
        Instance(WidgetComponent), depends_on='children',
    )

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

    #: How strongly a component hugs it's contents' width. Scroll
    #: areas do not hug their width and are free to expand.
    hug_width = 'ignore'

    #: How strongly a component hugs it's contents' height. Scroll
    #: areas do not hug their height and are free to expand.
    hug_height = 'ignore'

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkScrollArea)
    
    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_scrolled_component(self):
        """ The property getter for the 'scrolled_component' attribute.

        """
        children = self.children
        n = len(children)
        if n == 0:
            res = None
        elif n == 1:
            res = children[0]
        else:
            msg = ('A ScrollArea can have at most 1 widget child. Got '
                   '%s instead.')
            raise ValueError(msg % n)
        return res
        
    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    @on_trait_change('scrolled_component, preferred_size')
    def _on_scroll_area_deps_changed(self):
        """ A change handler which requests a relayout when the scrolled
        component or the preferred size changes, provided that the 
        component is initialized.

        """
        if self.initialized:
            self.request_relayout()

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def _setup_finalize(self):
        """ Overridden setup method to set the min size of the component
        once its layout has been initialized.

        """
        super(ScrollArea, self)._setup_finalize()
        self.update_min_scrolled_size()

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def size_hint(self):
        """ A reimplemented parent class method which uses the given 
        preferred size when computing the size hint, but falls back
        to the default implementation if a preferred is not given.

        """
        # TODO - We probably want to honor the hug and clip properties
        # on the scrolled component when computing its size hint. This
        # will allow any Container in which we may be embedded to 
        # compute an appropriate size hint from ours.
        width, height = self.preferred_size
        width_hint, height_hint = super(ScrollArea, self).size_hint()
        if width is None:
            width = width_hint
        if height is None:
            height = height_hint
        return Size(width, height)

    def do_relayout(self):
        """ A reimplemented LayoutTaskHandler handler method which will
        perform necessary update activity when a relayout it requested.

        """
        # This method is called whenever a relayout is requested.
        # We update the size of the scrolled components and fire 
        # off a size hint updated event so that the parent can
        # peform a relayout.
        self.update_min_scrolled_size()
        self.size_hint_updated()

    def update_min_scrolled_size(self):
        """ Updates the minimum size of the scrolled component with its
        computed minimum size, or its size hint.

        """
        scrolled = self.scrolled_component
        if scrolled is not None:
            if isinstance(scrolled, Container):
                min_size = scrolled.compute_min_size()
            else:
                min_size = scrolled.size_hint()
            scrolled.set_min_size(min_size)

