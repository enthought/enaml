#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import (
    List, Enum, Unicode, Bool, Instance, Property, cached_property,
)

from .widget_component import WidgetComponent, AbstractTkWidgetComponent


class AbstractTkDockPane(AbstractTkWidgetComponent):
    
    @abstractmethod
    def shell_title_changed(self, title):
        raise NotImplementedError
    
    @abstractmethod
    def shell_vertical_title_changed(self, vertical):
        raise NotImplementedError
    
    @abstractmethod
    def shell_closable_changed(self, closable):
        raise NotImplementedError
    
    @abstractmethod
    def shell_movable_changed(self, movable):
        raise NotImplementedError
    
    @abstractmethod
    def shell_floatable_changed(self, floatable):
        raise NotImplementedError
    
    @abstractmethod
    def shell_allowed_areas_changed(self, allowed_areas):
        raise NotImplementedError
    
    @abstractmethod
    def shell_dock_widget_changed(self, dock_widget):
        raise NotImplementedError


class DockPane(WidgetComponent):
    """ A widget which holds a single child component and can be used
    as a movable dock panel in a MainWindow.

    """
    #: The title of the dock area.
    title = Unicode

    #: Whether or not the title bar is displayed vertically.
    vertical_title = Bool(False)

    #: Whether or not the dock area is closable via a close button.
    closable = Bool(True)

    #: Whether or not the dock area is movable from its current position.
    movable = Bool(True)

    #: Whether or not the dock are is floatable as a separate window.
    floatable = Bool(True)
    
    #: The areas in the main window in which this dock area is allowed.
    allowed_areas = List(
        Enum('left', 'right', 'top', 'bottom', 'all'), value=['all'],
    )

    #: The widget being managed by the dock area.
    dock_widget = Property(
        Instance(WidgetComponent), depends_on='children',
    )

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkDockPane)

    def _setup_finalize(self):
        super(DockPane, self)._setup_finalize()
        ms = self.dock_widget.compute_min_size()
        print 'min size', ms
        self.dock_widget.set_min_size(ms)
    
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

