#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance

from .container import Container
from .menu_bar import MenuBar
from .window import Window, AbstractTkWindow

from ..core.trait_types import EnamlEvent, EnamlWidgetInstance
from ..layout.geometry import Size
from ..noncomponents.abstract_dock_manager import AbstractTkDockManager


class AbstractTkMainWindow(AbstractTkWindow):
    """ The abstract toolkit interface for a MainWindow.

    """
    @abstractmethod
    def shell_menu_bar_changed(self, menu_bar):
        """ Update the window's menu bar with the provide Enaml MenuBar
        instance.

        """
        raise NotImplementedError


class MainWindow(Window):
    """ A top-level main window widget.

    MainWindow widgets are top-level widgets which provide various frame 
    decorations and other window related functionality. A window may 
    optionally contain a menubar, any number of toolbars, a status bar,
    and dock panes. A window can have at most one central widget child
    which will be expanded to fit the available space of the window.
    
    Sizing information relates to the size of the central widget rather
    than the overall size of the window. That is, specifying a minimum
    size for a MainWindow is akin to specifying a minimum size for the
    central widget. The space consumed by dock panes and menus is in
    addition to this space.

    """
    #: The menu bar for the window. This widget is automatically setup
    #: and destroyed when assigned to this attribute. Instances should
    #: therefore not be reused, but created on-the-fly as needed.
    menu_bar = EnamlWidgetInstance(MenuBar)
    
    #: The dock manager used for this main window.
    dock_manager = Instance(AbstractTkDockManager)

    #: An event which is fired when the window is closed.
    closed = EnamlEvent

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkMainWindow)

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def _setup_finalize(self):
        """ A setup method which assigns the dock manager a reference 
        to this MainWindow instance.

        """
        super(MainWindow, self)._setup_finalize()
        self._set_dock_manager_window()

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def _dock_manager_changed(self):
        """ The change handler for the 'dock_manager' attribute which 
        updates the dock manager with the current MainWindow reference.

        """
        self._set_dock_manager_window()
    
    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def resize_to_initial(self):
        """ Overridden parent class method which resizes the window to 
        the initial size according to the semantics required of a main
        window.

        If the value of the 'initial_size' attribute is (-1, -1), then
        the initiali size of the window is determined by using the size
        hint of the central widget. Otherwise, the given 'initial_size'
        is used. 

        Note: If any dock panels or toolbars are in use, then this 
           computed initial size will likely be smaller than the 
           allowable minimum size, and therefore the minimum size
           will end up being the initial size. This is usually 
           the desired behavior. If the off chance that it isn't
           then manually specifying an initial size *and* a minimum
           size is sufficient to override the default behavior.
        
        """
        if self.initialized:
            init_size = self.initial_size
            if init_size == (-1, -1):
                widget = self.central_widget
                if widget is not None:
                    init_size = widget.size_hint()
                    self.resize(Size(*init_size))
            else:
                self.resize(Size(*init_size))

    def update_minimum_size(self):
        """ Overridden parent class method which updates the minimum size
        according the semantics required for a main window.

        If the value of the 'minimum_size' attribute is (-1, -1), then
        the minimum size of the window is indirectly using the minimum
        size of the central widget. That is, the minimum size of the 
        main window will be large enough to accomodate the minimum size
        of the central widget plus whatever dock panels, menu bars, and
        tool bars are in use. If the 'minimum_size' attribute is set to
        something other than (-1, -1), then that value will be used as
        the minimum size for the *entire* window, without regard to any
        dock panels etc. that are in use. The default behavior is 
        usually what is desired in most applications.

        Note: The minimum size computation for a MainWindow does not
            make use of the 'minimum_size_default' attribute.

        """
        if self.initialized:
            min_size = self.minimum_size
            if min_size == (-1, -1):
                self._update_central_widget_min_size()
            else:
                self.set_min_size(Size(*min_size))

    def resize_to_minimum(self):
        """ Overridden parent class method which resizes the window to
        the minimum size, respecting the semantics of a main window.

        """
        if self.initialized:
            min_size = self.minimum_size
            if min_size == (-1, -1):
                min_size = self._update_central_widget_min_size()
                if min_size != (-1, -1):
                    self.resize(min_size)
            else:
                min_size = Size(*min_size)
                self.set_min_size(min_size)
                self.resize(min_size)

    def update_maximum_size(self):
        """ Overridden parent class method which updates the maximum size
        according the semantics required for a main window.

        If the value of the 'maximum_size' attribute is (-1, -1), then
        the maximum size of the window is limits allowed by most GUI 
        toolkits. That is, the maximum size of the central widget is 
        ignored, and it will be expanded to fit the available space in
        the window. This is distinctly different from the maximum size
        computation in a Window, where the maximum size of the central
        widget is respected. Respecting this max size in a MainWindow 
        is not supported since it would lead to unituitive interactions
        between the sizing of the central widget and any dock panels 
        that are in use.

        Note: The maximum size computation for a MainWindow does not
            make use of the 'minimum_size_default' attribute.

        """
        if self.initialized:
            max_size = self.maximum_size
            if max_size == (-1, -1):
                v = 2**24 - 1
                max_size = (v, v)
            self.set_max_size(Size(*max_size))

    def resize_to_maximum(self):
        """ Overridden parent class method which resizes the window to
        the maximum size, respecting the semantics of a main window.

        """
        if self.initialized:
            max_size = self.maximum_size
            if max_size == (-1, -1):
                v = 2**24 - 1
                max_size = (v, v)
            max_size = Size(*max_size)
            self.set_max_size(max_size)
            self.resize(max_size)
    
    #--------------------------------------------------------------------------
    # Helper Methods
    #--------------------------------------------------------------------------
    def _set_dock_manager_window(self):
        """ Supplies the current dock manager with a reference to this
        MainWindow instance.

        """
        mgr = self.dock_manager
        if mgr is not None:
            mgr.main_window = self

    def _update_central_widget_min_size(self):
        """ Computes, applies, and returns the minimum size for the 
        central widget.

        Returns
        -------
        result : Size
            The computed minimum Size instance for the central widget.
            If the central widget is None, the return value will be 
            Size(-1, -1).

        """
        widget = self.central_widget
        if widget is not None:
            if isinstance(widget, Container):
                min_size = Size(*widget.compute_min_size())
            else:
                min_size = Size(*widget.size_hint())
            widget.set_min_size(min_size)
        else:
            min_size = Size(-1, -1)
        return min_size

