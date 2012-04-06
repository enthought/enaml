#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import (
    List, Enum, Unicode, Bool, Instance, Property, cached_property,
)

from .container import Container
from .layout_task_handler import LayoutTaskHandler
from .widget_component import WidgetComponent, AbstractTkWidgetComponent

from ..core.trait_types import EnamlEvent


class AbstractTkDockPane(AbstractTkWidgetComponent):
    """ The abstract toolkit interface for a DockPane.

    """
    @abstractmethod
    def shell_title_changed(self, title):
        """ Updates the title bar text in the dock pane.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_closable_changed(self, closable):
        """ Updates whether or not the dock pane should have a close
        button in the title bar.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_movable_changed(self, movable):
        """ Updates whether or not the dock pane should be movable from
        its current position.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_floatable_changed(self, floatable):
        """ Updates whether or not the dock pane is allowed to be 
        undocked an floated over the main window.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_floating_changed(self, floating):
        """ Updates whether or no the dock pane is floating over
        the main window instead of docked in its area.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_title_bar_orientation_changed(self, orientation):
        """ Updates the orientation of the title bar.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_allowed_dock_areas_changed(self, allowed_areas):
        """ Updates the allowable docking areas for the dock pane.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_dock_widget_changed(self, dock_widget):
        """ Updates the widget being managed by the dock pane.

        """
        raise NotImplementedError


class DockPane(LayoutTaskHandler, WidgetComponent):
    """ A DockPane is a widget which holds a single child component and 
    can be provided to a DockManager in a MainWindow so that it may
    be docked in the window's various docking areas.

    A dock pane contains a title bar with an optional close button.
    When a dock pane is closed, it is not destroyed. Rather it's 
    visibility is set to False and it consumes zero space in the 
    dock area. To fully remove a dock pane from a window, it must
    be removed from the dock manager.

    """
    #: The title of the dock area.
    title = Unicode

    #: Whether or not the dock area is closable via a close button.
    closable = Bool(True)

    #: Whether or not the dock area is movable from its current position.
    movable = Bool(True)

    #: Whether or not the dock are is floatable as a separate window.
    floatable = Bool(True)
    
    #: A boolean indicating whether or not the dock pane is floating.
    floating = Bool(False)

    #: The orientation of the title bar.
    title_bar_orientation = Enum('horizontal', 'vertical')

    #: The dock area in which the pane currently resides.
    dock_area = Enum('left', 'right', 'top', 'bottom')

    #: The areas in the main window in which this dock area is allowed
    #: to be docked via user interaction.
    allowed_dock_areas = List(
        Enum('left', 'right', 'top', 'bottom', 'all'), value=['all'],
    )

    #: The widget being managed by the dock area.
    dock_widget = Property(
        Instance(WidgetComponent), depends_on='children',
    )

    #: An event that is emitted whenever the dock pane is moved from
    #: its current dock location to another dock location. The event
    #: payload will be a tuple of (old_area, new_area). If the pane
    #: is moved to a new location in the same area, then the old
    #: area will be the same as the new area.
    moved = EnamlEvent

    #: An event that is emitted whenever the dock pane is undocked
    #: and becomes a floating pane.
    undocked = EnamlEvent

    #: An event that is emitted whenever the floating dock pane
    #: is docked in a dock area.
    docked = EnamlEvent 

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkDockPane)
    
    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_dock_widget(self):
        """ The property getter for the 'dock_widget' attribute.

        """
        flt = lambda child: isinstance(child, WidgetComponent)
        widgets = filter(flt, self.children)
        n = len(widgets)
        if n != 1:
            msg = ('A DockPane must have exactly 1 child widget. '
                   'Got %s instead.')
            raise ValueError(msg % n)
        else:
            res = widgets[0]
        return res

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def _setup_finalize(self):
        """ Updates the minimum size of the underlying dock widget during
        the finalization pass of the setup.

        """
        super(DockPane, self)._setup_finalize()
        self._update_dock_widget_min_size()

    #--------------------------------------------------------------------------
    # Layout Handling
    #--------------------------------------------------------------------------
    def do_relayout(self):
        """ A reimplemented LayoutTaskHandler handler method which will
        perform necessary update activity when a relayout it requested.

        """
        self._update_dock_widget_min_size()

    #--------------------------------------------------------------------------
    # Auxiliary Methods
    #--------------------------------------------------------------------------
    def _update_dock_widget_min_size(self):
        """ Updates the minimum size of the underlying dock widget based
        on its computed value if it's a Container, or its size hint 
        otherwise.

        """
        widget = self.dock_widget
        if isinstance(widget, Container):
            min_size = widget.compute_min_size()
        else:
            min_size = widget.size_hint()
        widget.set_min_size(min_size)

