from traits.api import implements

from .qt_line_edit import QtLineEdit

from ..field import IFieldImpl


class QtField(QtLineEdit):
    """ A PySide implementation of IField.

    QtField is a subclass of QtLineEdit.

    See Also
    --------
    IField

    """
    implements(IFieldImpl)

    #---------------------------------------------------------------------------
    # IFieldImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
