#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtCore, QtGui
from .qt_container import QtContainer
from .qt_resizing_widgets import QResizingScrollArea

from ..scroll_area import AbstractTkScrollArea


SCROLLBAR_POLICY_MAP = dict(
    as_needed=QtCore.Qt.ScrollBarAsNeeded,
    always_off=QtCore.Qt.ScrollBarAlwaysOff,
    always_on=QtCore.Qt.ScrollBarAlwaysOn,
)


class QtScrollArea(QtContainer, AbstractTkScrollArea):
    """ Qt implementation of the ScrollArea Container.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QScrollAreacontrol.

        """
        self.widget = QResizingScrollArea(self.parent_widget())

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtScrollArea, self).initialize()
        self.widget.setWidgetResizable(True)
        shell = self.shell_obj
        self._set_horiz_policy(shell.horizontal_scrollbar_policy)
        self._set_vert_policy(shell.vertical_scrollbar_policy)
        self._update_children()

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_horizontal_scrollbar_policy_changed(self, policy):
        """ The change handler for the 'horizontal_scrollbar_policy'
        attribute of the shell object.

        """
        self._set_horiz_policy(policy)

    def shell_vertical_scrollbar_policy_changed(self, policy):
        """ The change handler for the 'vertical_scrollbar_policy'
        attribute of the shell object.

        """
        self._set_vert_policy(policy)

    def shell_children_changed(self, children):
        """ The change handler for the children of the shell object.

        """
        self._update_children()

    def shell_children_items_changed(self, event):
        """ The change handler for the children items event of the
        shell object.

        """
        # XXX this won't work because traits does not properly hook
        # up items event listeners via calls to .add_trait_listener
        # which is how this object has been hooked up.
        self._update_children()
    
    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state. This
        value is used by the layout manager to determine how much
        space to allocate the widget.

        Overriden to ask the child widget for its size hint. Fall back 
        to the minimum size if there is no size hint. If we use a 
        constraints-based Container as the child widget, it will only have
        a minimum size set, not a size hint.

        """
        child = self.widget.widget()
        if child is None:
            # use the QAbstractScrollArea default size hint
            return (256, 192)

        size_hint = child.sizeHint()
        if not size_hint.isValid():
            size_hint = child.minimumSize()

        # Add scrollbar extents to allow room for the scrollbars.
        width = size_hint.width()
        height = size_hint.height()
        style = self.widget.style()
        options = QtGui.QStyleOptionSlider()
        options.orientation = QtCore.Qt.Horizontal
        # FIXME: the 2 is magical and may be entirely OS X 10.7-specific.
        height += style.pixelMetric(style.PM_ScrollBarExtent, options) + 2
        options.orientation = QtCore.Qt.Vertical
        width += style.pixelMetric(style.PM_ScrollBarExtent, options) + 2
        
        return (width, height)

    #--------------------------------------------------------------------------
    # Widget Update
    #--------------------------------------------------------------------------
    def _set_horiz_policy(self, policy):
        """ Set the horizontal scrollbar policy of the widget.

        """
        self.widget.setHorizontalScrollBarPolicy(SCROLLBAR_POLICY_MAP[policy])

    def _set_vert_policy(self, policy):
        """ Set the vertical scrollbar policy of the widget.

        """
        self.widget.setVerticalScrollBarPolicy(SCROLLBAR_POLICY_MAP[policy])
   
    def _update_children(self):
        """ Update the QScrollArea's children with the current children.

        """
        shell = self.shell_obj
        if len(shell.children) == 0:
            self.widget.setWidget(None)
        else:
            self.widget.setWidget(shell.children[0].toolkit_widget)

