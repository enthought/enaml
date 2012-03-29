#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QDockWidget
from .qt.QtCore import Qt
from .qt_widget_component import QtWidgetComponent

from ...components.dock_pane import AbstractTkDockPane


DOCK_AREA_MAP = {
    'left': Qt.LeftDockWidgetArea,
    'right': Qt.RightDockWidgetArea,
    'top': Qt.TopDockWidgetArea,
    'bottom': Qt.BottomDockWidgetArea,
    'all': Qt.AllDockWidgetAreas,
}


class QtDockPane(QtWidgetComponent, AbstractTkDockPane):
    """ A Qt4 implementation of DockPane.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        self.widget = QDockWidget(parent)

    def initialize(self):
        super(QtDockPane, self).initialize()
        shell = self.shell_obj
        self.set_title(shell.title)
        self.set_vertical_title(shell.vertical_title)
        self.set_closable(shell.closable)
        self.set_movable(shell.movable)
        self.set_floatable(shell.floatable)
        self.set_allowed_areas(shell.allowed_areas)
        self.set_dock_widget(shell.dock_widget)

    #--------------------------------------------------------------------------
    # Shell Object Change Handlers
    #--------------------------------------------------------------------------
    def shell_title_changed(self, title):
        self.set_title(title)
            
    def shell_vertical_title_changed(self, vertical_title):
        self.set_vertical_title(vertical_title)
        
    def shell_closable_changed(self, closable):
        self.set_closable(closable)
            
    def shell_movable_changed(self, movable):
        self.set_movable(movable)
            
    def shell_floatable_changed(self, floatable):
        self.set_floatable(floatable)

    def shell_allowed_areas_changed(self, allowed_areas):
        self.set_allowed_areas(allowed_areas)
            
    def shell_dock_widget_changed(self, dock_widget):
        self.set_dock_widget(dock_widget)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_title(self, title):
        self.widget.setWindowTitle(title)
    
    def set_vertical_title(self, vertical_title):
        tag = QDockWidget.DockWidgetVerticalTitleBar
        self._update_feature_tag(tag, vertical_title)

    def set_closable(self, closable):
        tag = QDockWidget.DockWidgetClosable
        self._update_feature_tag(tag, closable)
    
    def set_movable(self, movable):
        tag = QDockWidget.DockWidgetMovable
        self._update_feature_tag(tag, movable)
    
    def set_floatable(self, floatable):
        tag = QDockWidget.DockWidgetFloatable
        self._update_feature_tag(tag, floatable)

    def set_allowed_areas(self, allowed_areas):
        flags = Qt.NoDockWidgetArea
        for area in allowed_areas:
            flags |= DOCK_AREA_MAP[area]
        self.widget.setAllowedAreas(flags)

    def set_dock_widget(self, dock_widget):
        self.widget.setWidget(dock_widget.toolkit_widget)
    
    #--------------------------------------------------------------------------
    # Auxiliary Methods
    #--------------------------------------------------------------------------
    def _update_feature_tag(self, tag, add=True):
        widget = self.widget
        features = widget.features()
        if add:
            features |= tag
        else:
            features &= ~tag
        widget.setFeatures(features)

