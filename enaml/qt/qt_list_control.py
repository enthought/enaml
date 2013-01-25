#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import QSize
from .qt.QtGui import QListWidget
from .qt_control import QtControl
from .qt_list_item import QtListItem


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
        self.set_icon_size(tree['icon_size'])

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
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_icon_size(self, size):
        """ Set the icon size on the underlying control.

        """
        self.widget().setIconSize(QSize(*size))


