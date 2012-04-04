#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QDockWidget
from .qt.QtCore import Qt, Signal
from .qt_widget_component import QtWidgetComponent
from .noncomponents.qt_dock_manager import DOCK_AREA_MAP

from ...components.dock_pane import AbstractTkDockPane


#: A mapping from Qt dock area enum values to Enaml dock area values.
DOCK_AREA_INVERSE_MAP = dict(
    (value, key) for (key, value) in DOCK_AREA_MAP.iteritems()
)


class QtDockWidget(QDockWidget):
    """ A QDockWidget subclass which converts a close event into a 
    closed signal.

    """
    closed = Signal()

    def closeEvent(self, event):
        super(QtDockWidget, self).closeEvent(event)
        self.closed.emit()


class QtDockPane(QtWidgetComponent, AbstractTkDockPane):
    """ A Qt4 implementation of DockPane.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QDockWidget instance.

        """
        self.widget = QtDockWidget(parent)

    def initialize(self):
        """ Initializes the attributes of the QDockWidget.

        """
        super(QtDockPane, self).initialize()
        shell = self.shell_obj
        self.set_title(shell.title)
        self.set_closable(shell.closable)
        self.set_movable(shell.movable)
        self.set_floatable(shell.floatable)
        self.set_floating(shell.floating)
        self.set_title_bar_orientation(shell.title_bar_orientation)
        self.set_allowed_dock_areas(shell.allowed_dock_areas)
        self.set_dock_widget(shell.dock_widget)

    def bind(self):
        """ Binds the signal handlers for the QDockWidget.

        """
        super(QtDockPane, self).bind()
        widget = self.widget
        widget.dockLocationChanged.connect(self.on_dock_location_changed)
        widget.topLevelChanged.connect(self.on_top_level_changed)
        widget.closed.connect(self.on_close)

    #--------------------------------------------------------------------------
    # Shell Object Change Handlers
    #--------------------------------------------------------------------------
    def shell_title_changed(self, title):
        """ Updates the title bar text in the dock pane.

        """
        self.set_title(title)
            
    def shell_closable_changed(self, closable):
        """ Updates whether or not the dock pane should have a close
        button in the title bar.

        """
        self.set_closable(closable)
            
    def shell_movable_changed(self, movable):
        """ Updates whether or not the dock pane should be movable from
        its current position.

        """
        self.set_movable(movable)
            
    def shell_floatable_changed(self, floatable):
        """ Updates whether or not the dock pane is allowed to be 
        undocked an floated over the main window.

        """
        self.set_floatable(floatable)

    def shell_floating_changed(self, floating):
        """ Updates whether or no the dock pane is floating over
        the main window instead of docked in its area.

        """
        self.set_floating(floating)

    def shell_title_bar_orientation_changed(self, orientation):
        """ Updates the orientation of the title bar.

        """
        self.set_title_bar_orientation(orientation)
        
    def shell_allowed_dock_areas_changed(self, allowed_areas):
        """ Updates the allowable docking areas for the dock pane.

        """
        self.set_allowed_dock_areas(allowed_areas)
            
    def shell_dock_widget_changed(self, dock_widget):
        """ Updates the widget being managed by the dock pane.

        """
        self.set_dock_widget(dock_widget)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_dock_location_changed(self, new_qarea):
        """ The signal handler for the 'dockLocationChanged' signal. It
        updates the 'dock_area' attribute on the shell object and fires
        off the 'moved' event.

        """
        shell = self.shell_obj
        old_area = shell.dock_area
        new_area = DOCK_AREA_INVERSE_MAP[new_qarea]
        shell.dock_area = new_area
        shell.moved((old_area, new_area))

    def on_top_level_changed(self, floating):
        """ The signal handler for the 'topLevelChanged' signal. It 
        fires of the 'moved' event and the appropriate 'docked' or
        'undocked' event on the shell object.

        """
        shell = self.shell_obj
        shell.floating = floating
        if floating:
            shell.undocked()
        else:
            shell.docked()

    def on_close(self):
        """ The signal handler for the 'closed' signal. It sets the
        visibility of the shell component to False.

        """
        self.shell_obj.visible = False

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Sets the title bar text of the dock widget.

        """
        self.widget.setWindowTitle(title)

    def set_closable(self, closable):
        """ Sets the closable flag of the title bar.

        """
        flag = QDockWidget.DockWidgetClosable
        self._update_feature_flag(flag, closable)
    
    def set_movable(self, movable):
        """ Sets the movable flag of the title bar.

        """
        flag = QDockWidget.DockWidgetMovable
        self._update_feature_flag(flag, movable)
    
    def set_floatable(self, floatable):
        """ Sets the floatable flag of the title bar.

        """
        flag = QDockWidget.DockWidgetFloatable
        self._update_feature_flag(flag, floatable)

    def set_floating(self, floating):
        """ Sets the whether or not the dock widget is floating.

        """
        widget = self.widget
        if widget.isFloating() != floating:
            widget.setFloating(floating)

    def set_title_bar_orientation(self, orientation):
        """ Sets the orientation flag of the title bar.

        """
        flag = QDockWidget.DockWidgetVerticalTitleBar
        self._update_feature_flag(flag, orientation == 'vertical')

    def set_allowed_dock_areas(self, allowed_areas):
        """ Sets the flags for the allowed docking areas.

        """
        flags = Qt.NoDockWidgetArea
        for area in allowed_areas:
            flags |= DOCK_AREA_MAP[area]
        self.widget.setAllowedAreas(flags)

    def set_dock_widget(self, dock_widget):
        """ Sets the widget being managed by the dock widget.

        """
        self.widget.setWidget(dock_widget.toolkit_widget)
    
    #--------------------------------------------------------------------------
    # Auxiliary Methods
    #--------------------------------------------------------------------------
    def _update_feature_flag(self, flag, add=True):
        """ Updates the feature flag for the dock widget.

        Parameters
        ----------
        flag : QDockWidget feature flag
            The feature flag to apply to the dock widget.
        
        add : bool, optional
            Whether to add or remove the flag from the dock widget 
            features. The default is True.
        
        """
        widget = self.widget
        features = widget.features()
        if add:
            features |= flag
        else:
            features &= ~flag
        widget.setFeatures(features)

