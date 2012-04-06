#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from weakref import ref

from ..qt.QtCore import Qt

from ....noncomponents.abstract_dock_manager import AbstractTkDockManager


#: A mapping from Enaml dock area values to Qt dock area enum values.
DOCK_AREA_MAP = {
    'left': Qt.LeftDockWidgetArea,
    'right': Qt.RightDockWidgetArea,
    'top': Qt.TopDockWidgetArea,
    'bottom': Qt.BottomDockWidgetArea,
    'all': Qt.AllDockWidgetAreas,
}


class QtDockManager(AbstractTkDockManager):
    """ 

    """
    def __init__(self, *dock_panes):
        """ Initialize a DockManager instance.

        Parameters
        ----------
        *dock_panes
            The initial DockPane instances to use with the manager.

        """
        self._panes = list(dock_panes)
        self._window_ref = lambda: None

    def _get_main_window(self):
        """ The property getter for the 'main_window' property.

        """
        return self._window_ref()
    
    def _set_main_window(self, window):
        """ The property setter for the 'main_window' property.

        """
        old_main = self._window_ref()
        self._window_ref = ref(window)
        if old_main is not None:
            old_main.dock_manager = None
        curr_panes = self._panes
        self._panes = []
        for pane in curr_panes:
            self.add_pane(pane)

    main_window = property(_get_main_window, _set_main_window)
                
    def add_pane(self, pane):
        """ Add a dock pane to the manager and hence the window.

        Parameters
        ----------
        pane : DockPane
            The DockPane instance to add to the manager. If the pane is
            already being managed, this method call is a no-op.
        
        """
        if pane not in self._panes:
            self._panes.append(pane)
            window = self._window_ref()
            if window is not None:
                qwindow = window.toolkit_widget
                if qwindow is not None:
                    if not pane.initialized:
                        pane.setup(qwindow)
                    qarea = DOCK_AREA_MAP[pane.dock_area]
                    qwindow.addDockWidget(qarea, pane.toolkit_widget)

    def remove_pane(self, pane):
        """ Remove a dock pane from the manager and hence the window.

        Parameters
        ----------
        pane : DockPane
            The DockPane instance to remove from the manager. If the
            pane is not being managed, this method call is a no-op.
        
        """
        if pane in self._panes:
            self._panes.remove(pane)
            window = self._window_ref()
            if window is not None:
                qwindow = window.toolkit_widget
                if qwindow is not None:
                    qwindow.removeDockWidget(pane.toolkit_widget)
    
    def panes(self):
        """ Get the list of dock panes currently being managed.

        Returns
        -------
        result : list
            The list of DockPane instance being managed by this manager.
        
        """
        return self._panes[:]

