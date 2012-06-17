#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QListView
from .qt_abstract_item_view import QtAbstractItemView

from ...components.list_view import AbstractTkListView


VIEW_MODE_MAP = {
    'list': QListView.ListMode,
    'icon': QListView.IconMode,
}


RESIZE_MODE_MAP = {
    'adjust': QListView.Adjust,
    'fixed': QListView.Fixed,
}


FLOW_MAP = {
    'left_to_right': QListView.LeftToRight,
    'top_to_bottom': QListView.TopToBottom,
}


class QtListView(QtAbstractItemView, AbstractTkListView):
    """ A Qt implementation of ListView.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying QListView control.

        """
        self.widget = QListView(parent)

    def initialize(self):
        """ Initialize the state of the underlying QListView.

        """
        super(QtListView, self).initialize()
        shell = self.shell_obj
        self.set_view_mode(shell.view_mode)
        self.set_resize_mode(shell.resize_mode)
        self.set_wrapping(shell.wrapping)
        self.set_flow(shell._flow)
        self.set_item_spacing(shell.item_spacing)
        self.set_uniform_item_sizes(shell.uniform_item_sizes)

    #--------------------------------------------------------------------------
    # Shell Object Change Handlers
    #--------------------------------------------------------------------------
    def shell_view_mode_changed(self, mode):
        """ The change handler for the 'view_mode' attribute on the
        shell object.

        """
        self.set_view_mode(mode)

    def shell_resize_mode_changed(self, mode):
        """ The change handler for the 'resize_mode' attribute on the
        shell object.

        """
        self.set_resize_mode(mode)

    def shell_wrapping_changed(self, wrapping):
        """ The change handler for the 'wrapping' attribute on the 
        shell object.

        """
        self.set_wrapping(wrapping)

    def shell__flow_changed(self, flow):
        """ The change handler for the '_flow' attribute on the 
        shell object.

        """
        self.set_flow(flow)

    def shell_item_spacing_changed(self, spacing):
        """ The change handler for the 'item_spacing' attribute on
        the shell object.

        """
        self.set_item_spacing(spacing)

    def shell_uniform_item_sizes_changed(self, uniform):
        """ The change handler for the 'uniform_item_sizes' attribute
        on the shell object.

        """
        self.set_uniform_item_sizes(uniform)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_view_mode(self, mode):
        """ Sets the view mode of the underlying widget.

        """
        qmode = VIEW_MODE_MAP[mode]
        self.widget.setViewMode(qmode)

    def set_resize_mode(self, mode):
        """ Sets the resize mode on the underlying widget.

        """
        qmode = RESIZE_MODE_MAP[mode]
        self.widget.setResizeMode(qmode)

    def set_wrapping(self, wrapping):
        """ Set the wrapping state of the underlying widget.

        """
        self.widget.setWrapping(wrapping)

    def set_flow(self, flow):
        """ Set the flow mode of the underlying widget.

        """
        qflow = FLOW_MAP[flow]
        self.widget.setFlow(qflow)

    def set_item_spacing(self, spacing):
        """ Sets the item spacing on the underlying widget.

        """
        self.widget.setSpacing(spacing)

    def set_uniform_item_sizes(self, uniform):
        """ Sets the uniform item sizes state on the underlying widget.

        """
        self.widget.setUniformItemSizes(uniform)

