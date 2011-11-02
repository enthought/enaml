#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_control import QtControl

from ..combo_box import AbstractTkComboBox


class QtComboBox(QtControl, AbstractTkComboBox):
    """ A Qt implementation of ComboBox.

    Use a combo box to select a single item from a collection of items.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates a QComboBox.

        """
        self.widget = QtGui.QComboBox(self.parent_widget())

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(QtComboBox, self).initialize()
        shell = self.shell_obj
        self.set_items(shell._labels)
        self.set_selection(shell._index)

    def bind(self):
        """ Connects the event handlers for the combo box.

        """
        super(QtComboBox, self).bind()
        self.widget.currentIndexChanged.connect(self.on_selected)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell__index_changed(self, index):
        """ The change handler for the _index attribute on the enaml shell.

        """
        shell = self.shell_obj
        self.set_selection(index)

    def shell_to_string_changed(self, value):
        """ The change handler for the 'string' attribute on the enaml
        shell.

        """
        self.update_items()

    def shell_items_changed(self, items):
        """ The change handler of 'items' attribute on the enaml shell.

        """
        self.update_items()

    def shell_items_items_changed(self, items):
        """ The change handler for the 'items' event of the 'items'
        attribute on the enaml shell.

        """
        self.update_items()

    def update_items(self):
        """ Update the QComboBox with items from the enaml shell.

        """
        shell = self.shell_obj
        old_selection = self.get_selection()
        self.selection_event(enable=False)
        self.set_items(shell._labels)
        self.selection_event()
        self.move_selection(old_selection)

    def on_selected(self, index):
        """ The event handler for a combo box selection event.

        """
        shell = self.shell_obj
        shell._index = index
        shell.selected = shell.value

    def set_items(self, str_items):
        """ Sets the items in the combo box.

        """
        widget = self.widget
        widget.clear()
        widget.addItems(str_items)

    def set_selection(self, index):
        """ Sets the value in the combo box, or resets the combo box
        if the value is not in the list of items.

        """
        widget = self.widget
        widget.setCurrentIndex(index)

    # FIXME: I found it easier to setup the selection move when the items
    # change in the widget side. The alternative will require that the
    # items attribute in the abstract class is a Property of List(Any)
    # And I was a little worried to try it.
    def move_selection(self, value):
        """ Move the selection to the index where the value exists.

        The method attempts to find the index of the value. Moving
        the index does not cause a selected event to be fired. If the
        value is not found then the selection is undefined.

        """
        shell = self.shell_obj
        widget = self.widget
        index = widget.findText(value)
        if index == -1:
            shell._index = index
        else:
            # we silently set the `_index` attribute since the selection
            # value has not changed
            shell.trait_setq(_index=index)
            self.selection_event(enable=False)
            self.set_selection(index)
            self.selection_event()

    def get_selection(self):
        """ Retrieve the current selected option from the widget.

        """
        widget = self.widget
        return widget.currentText()

    def selection_event(self, enable=True):
        """ Enable/Disable the on selected event firing at the combo box.

        Since any change in the widget variables will cause a event it is
        necessary to temporarly disable the on_selected notifier method
        while the internal data are sycnronized between the component and
        the Qt widget.

        """
        if enable:
            self.widget.currentIndexChanged.connect(self.on_selected)
        else:
            self.widget.currentIndexChanged.disconnect(self.on_selected)
