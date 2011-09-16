from traits.api import implements

from .qt_line_edit import QtLineEdit

from ..field import IFieldImpl


class QtField(QtLineEdit):
    """ A PySide implementation of Field.

    QtField is a subclass of QtLineEdit.

    See Also
    --------
    Field

    """
    implements(IFieldImpl)

    #---------------------------------------------------------------------------
    # IFieldImpl interface
    #---------------------------------------------------------------------------
    def initialize_widget(self):
        """ Initializes the attributes of the field.

        """
        super(QtField, self).initialize_widget()
        self.sync_text()

    def parent_from_string_changed(self, from_string):
        """ The change handler for the 'from_string' attribute on parent.

        """
        self.sync_value()
    
    def parent_to_string_changed(self, to_string):
        """ The change handler for the 'to_string' attribute on parent.

        """
        self.sync_text()
    
    def parent_value_changed(self, value):
        """ The change hadnler for the 'value' attribute on parent.

        """
        self.sync_text()
    
    def parent_text_changed(self, text):
        """ The change handler for the 'text' attribute on parent.

        """
        super(QtField, self).parent_text_changed(text)
        self.sync_value()

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def sync_value(self):
        """ Synchronizes the 'value' attribute on the parent with the
        'text' attribute by making the appropriate conversion from 
        'text' to 'value' and handling any exceptions that arise.

        """
        parent = self.parent
        text = parent.text
        from_string = parent.from_string
        try:
            value = from_string(text)
        except Exception as e:
            parent.exception = e
            parent.error = True
        else:
            parent.exception = None
            parent.error = False
            parent.value = value
    
    def sync_text(self):
        """ Synchronizes the 'text' attribute on the parent with the
        'value' attribute by making the appropriate conversion from 
        'value' to 'text' and handling any exceptions that arise.

        """
        parent = self.parent
        value = parent.value
        to_string = parent.to_string
        try:
            text = to_string(value)
        except Exception as e:
            parent.exception = e
            parent.error = True
        else:
            parent.exception = None
            parent.error = False
            parent.text = text

