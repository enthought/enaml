#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import QSize
from .qt.QtGui import QListWidget
from .qt_control import QtControl
from .qt_list_item import QtListItem


VIEW_MODES = {
    'list': QListWidget.ListMode,
    'icon': QListWidget.IconMode,
}


RESIZE_MODES = {
    'adjust': QListWidget.Adjust,
    'fixed': QListWidget.Fixed,
}


LAYOUT_MODES = {
    'single_pass': QListWidget.SinglePass,
    'batched': QListWidget.Batched,
}


FLOW = {
    'left_to_right': QListWidget.LeftToRight,
    'top_to_bottom': QListWidget.TopToBottom,
}


class QtListControl(QtControl):
    """ A Qt implementation of an Enaml ListControl.

    """
    def create_widget(self, parent, tree):
        """ Create the underlying widget.

        """
        return QListWidget(parent)

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(QtListControl, self).create(tree)
        self.set_view_mode(tree['view_mode'])
        self.set_resize_mode(tree['resize_mode'])
        self.set_flow(tree['flow'])
        self.set_item_wrap(tree['item_wrap'])
        self.set_word_wrap(tree['word_wrap'])
        self.set_item_spacing(tree['item_spacing'])
        self.set_icon_size(tree['icon_size'])
        self.set_uniform_item_sizes(tree['uniform_item_sizes'])
        self.set_layout_mode(tree['layout_mode'])
        self.set_batch_size(tree['batch_size'])

    def init_layout(self):
        """ Initialize the layout of the underlying control.

        """
        super(QtListControl, self).init_layout()
        widget = self.widget()
        kids = [c for c in self.children() if isinstance(c, QtListItem)]
        for child in kids:
            widget.addItem(child.create_item())
        for child in kids:
            child.initialize_item()
        # Late-bind the signal handlers to avoid doing any unnecessary
        # work while the child items are being intialized.
        widget.itemChanged.connect(self.on_item_changed)
        widget.itemClicked.connect(self.on_item_clicked)
        widget.itemDoubleClicked.connect(self.on_item_double_clicked)

    def child_removed(self, child):
        """ Handle the child removed event for a QtListControl.

        """
        if not self._destroying and isinstance(child, QtListItem):
            widget = self.widget()
            item = child.item()
            if item is not None:
                row = widget.row(item)
                widget.takeItem(row)

    def child_added(self, child):
        """ Handle the child added event for a QtListControl.

        """
        if isinstance(child, QtListItem):
            row = self.index_of(child)
            item = child.create_item()
            self.widget().insertItem(row, item)
            child.initialize_item()

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_item_changed(self, item):
        """ The signal handler for the `itemChanged` signal.

        This handler forwards the call to the item that was changed.

        """
        owner = getattr(item, 'item_owner', None)
        if owner is not None:
            owner.on_changed()

    def on_item_clicked(self, item):
        """ The signal handler for the `itemClicked` signal.

        This handler forwards the call to the item that was clicked.

        """
        owner = getattr(item, 'item_owner', None)
        if owner is not None:
            owner.on_clicked()

    def on_item_double_clicked(self, item):
        """ The signal handler for the `itemDoubleClicked` signal.

        This handler forwards the call to the item that was clicked.

        """
        owner = getattr(item, 'item_owner', None)
        if owner is not None:
            owner.on_double_clicked()

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_refresh_items_layout(self, content):
        """ Handle the 'refresh_items_layout' action from the Enaml
        widget.

        """
        self.widget().scheduleDelayedItemsLayout()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_view_mode(self, mode):
        """ Set the view mode of the underlying control.

        """
        self.widget().setViewMode(VIEW_MODES[mode])
        self.widget().setMovement(QListWidget.Static)

    def set_resize_mode(self, mode):
        self.widget().setResizeMode(RESIZE_MODES[mode])

    def set_flow(self, flow):
        if flow == 'default':
            if self.widget().viewMode() == QListWidget.ListMode:
                qflow = QListWidget.TopToBottom
            else:
                qflow = QListWidget.LeftToRight
        else:
            qflow = FLOW[flow]
        self.widget().setFlow(qflow)

    def set_item_wrap(self, wrap):
        if wrap is None:
            wrap = self.widget().viewMode() == QListWidget.IconMode
        self.widget().setWrapping(wrap)

    def set_word_wrap(self, wrap):
        self.widget().setWordWrap(wrap)

    def set_item_spacing(self, spacing):
        self.widget().setSpacing(spacing)

    def set_icon_size(self, size):
        """ Set the icon size on the underlying control.

        """
        self.widget().setIconSize(QSize(*size))

    def set_uniform_item_sizes(self, uniform):
        self.widget().setUniformItemSizes(uniform)

    def set_layout_mode(self, mode):
        self.widget().setLayoutMode(LAYOUT_MODES[mode])

    def set_batch_size(self, size):
        self.widget().setBatchSize(size)



