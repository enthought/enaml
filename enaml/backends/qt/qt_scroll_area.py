#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtCore, QtGui
from .qt_constraints_widget import QtConstraintsWidget

from ...components.scroll_area import AbstractTkScrollArea


SCROLLBAR_POLICY_MAP = dict(
    as_needed=QtCore.Qt.ScrollBarAsNeeded,
    always_off=QtCore.Qt.ScrollBarAlwaysOff,
    always_on=QtCore.Qt.ScrollBarAlwaysOn,
)


class QtScrollArea(QtConstraintsWidget, AbstractTkScrollArea):
    """ Qt implementation of a ScrollArea.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QScrollAreacontrol.

        """
        self.widget = QtGui.QScrollArea(parent)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtScrollArea, self).initialize()
        self.widget.setWidgetResizable(True)
        shell = self.shell_obj
        self.set_horizontal_policy(shell.horizontal_scrollbar_policy)
        self.set_vertical_policy(shell.vertical_scrollbar_policy)
        self.update_scrolled_component()

    #--------------------------------------------------------------------------
    # Shell Object Change Handlers
    #--------------------------------------------------------------------------
    def shell_horizontal_scrollbar_policy_changed(self, policy):
        """ The change handler for the 'horizontal_scrollbar_policy'
        attribute of the shell object.

        """
        self.set_horizontal_policy(policy)

    def shell_vertical_scrollbar_policy_changed(self, policy):
        """ The change handler for the 'vertical_scrollbar_policy'
        attribute of the shell object.

        """
        self.set_vertical_policy(policy)

    def shell_scrolled_component_changed(self, component):
        """ The change handler for the 'layout_children' attribute of 
        the shell object.

        """
        self.update_scrolled_component()

    def vertical_scrollbar_thickness(self):
        """ Returns the pixel thickness of the scrollbar.

        """
        return self._scrollbar_thickness(QtCore.Qt.Vertical)
    
    def horizontal_scrollbar_thickness(self):
        """ Returns the pixel thickness of the scrollbar.

        """
        return self._scrollbar_thickness(QtCore.Qt.Vertical)

    def scroll_to_position(self, position, margin):
        """ Scrolls the area such that position is visible with a
        minimum of margin points surrounding position.

        """
        widget = self.widget

        pos_x, pos_y = position
        margin_x, margin_y = margin

        widget.ensureVisible(pos_x, pos_y, margin_x, margin_y)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_horizontal_policy(self, policy):
        """ Set the horizontal scrollbar policy of the widget.

        """
        self.widget.setHorizontalScrollBarPolicy(SCROLLBAR_POLICY_MAP[policy])

    def set_vertical_policy(self, policy):
        """ Set the vertical scrollbar policy of the widget.

        """
        self.widget.setVerticalScrollBarPolicy(SCROLLBAR_POLICY_MAP[policy])
    
    def update_scrolled_component(self):
        """ Update the QScrollArea's children with the current children.

        """
        component = self.shell_obj.scrolled_component
        if component is None:
            self.widget.setWidget(None)
        else:
            self.widget.setWidget(component.toolkit_widget)

    #--------------------------------------------------------------------------
    # Auxiliary Methods
    #--------------------------------------------------------------------------
    def _scrollbar_thickness(self, orientation):
        """ Returns the thickness of a scrollbar for the given orientation.

        """
        style = self.widget.style()
        options = QtGui.QStyleOptionSlider()
        options.orientation = orientation
        return style.pixelMetric(style.PM_ScrollBarExtent, options)

