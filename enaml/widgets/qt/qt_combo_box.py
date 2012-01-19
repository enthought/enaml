#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_control import QtControl

from ..combo_box import AbstractTkComboBox

from ...guard import guard


class QtComboBox(QtControl, AbstractTkComboBox):
    """ A Qt implementation of ComboBox.

    Use a combo box to select a single item from a collection of items.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates a QComboBox.

        """
        self.widget = QtGui.QComboBox(parent)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtComboBox, self).initialize()
        shell = self.shell_obj
        self.set_items(shell.labels)
        self.set_selection(shell.index)

    def bind(self):
        """ Connects the event handlers for the combo box.

        """
        super(QtComboBox, self).bind()
        self.widget.currentIndexChanged.connect(self.on_selected)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_index_changed(self, index):
        """ The change handler for the 'index' attribute on the shell
        object.

        """
        self.set_selection(index)

    def shell_labels_changed(self, labels):
        """ The change handler for the 'labels' attribute on the shell
        object.

        """
        self.set_items(labels)

    def on_selected(self):
        """ The event handler for a combo box selection event.

        """
        if not guard.guarded(self, 'updating'):
            shell = self.shell_obj
            curr_index = self.widget.currentIndex()
            shell.index = curr_index

            # Only fire the selected event if we have a valid selection
            if curr_index != -1:
                shell.selected(shell.value)

    def set_items(self, str_items):
        """ Sets the items in the combo box.

        """
        # We need to avoid a feedback loop when updating the items in 
        # the combo box. Qt will emit index changed signals when the 
        # items are updated. But, the shell object has already computed
        # the proper index for the new items, so we use that to update
        # the index of the control after updating the items. The flag
        # is read by the on_selected handler to ignore updates during
        # this process.
        with guard(self, 'updating'):
            widget = self.widget
            widget.clear()
            widget.addItems(str_items)
            widget.setCurrentIndex(self.shell_obj.index)

    def set_selection(self, index):
        """ Sets the value in the combo box, or resets the combo box
        if the value is not in the list of items.

        """
        # We need to avoid a feedback loop when updating the selection
        # in the combo box. Qt will emit index changed signals when the 
        # selectino is updated. But, the shell object has already computed
        # the proper index for the new selection so we don't need to feed
        # back while doing this.
        with guard(self, 'updating'):
            self.widget.setCurrentIndex(index)

