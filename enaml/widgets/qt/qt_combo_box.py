from .qt_api import QtGui

from traits.api import implements

from .qt_control import QtControl

from ..combo_box import IComboBoxImpl


class QtComboBox(QtControl):
    """ A PySide implementation of ComboBox.

    Use a combo box to select a single item from a collection of items. 
    
    See Also
    --------
    ComboBox

    """
    implements(IComboBoxImpl)

    #---------------------------------------------------------------------------
    # IComboBoxImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates a QComboBox.

        """
        self.widget = QtGui.QComboBox(self.parent_widget())

    def initialize_widget(self):
        """ Intializes the widget with the attributes of this instance.

        """
        self.items_changed()
        self.bind()
    
    def parent_value_changed(self, value):
        """ The change handler for the 'value' attribute on the parent.

        """
        self.set_value(value)

    def parent_to_string_changed(self, value):
        """ The change handler for the 'string' attribute on the parent.

        """
        self.items_changed()
    
    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def items_changed(self):
        """ Update the QComboBox with items from `parent`.
        
        """
        parent = self.parent
        str_items = map(parent.to_string, parent.items)
        self.set_items(str_items)

    def bind(self):
        """ Binds the event handlers for the combo box.

        """
        self.widget.currentIndexChanged.connect(self.on_selected)

    def on_selected(self):
        """ The event handler for a combo box selection event.

        """
        parent = self.parent
        idx = self.widget.currentIndex()
        value = parent.items[idx]
        parent.value = value
        parent.selected = value

    def set_items(self, str_items):
        """ Sets the items in the combo box.

        """
        widget = self.widget
        widget.clear()
        widget.addItems(str_items)

    def set_value(self, value):
        """ Sets the value in the combo box, or resets the combo box
        if the value is not in the list of items.

        """
        widget = self.widget
        str_value = self.parent.to_string(value)
        index = widget.findText(str_value)
        widget.setCurrentIndex(index)

