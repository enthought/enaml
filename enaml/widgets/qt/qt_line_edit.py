from traits.api import implements

from .qt_control import QtControl

from ..line_edit import ILineEditImpl


class QtLineEdit(QtControl):
    """ A PySide implementation of a LineEdit.

    See Also
    --------
    LineEdit

    """
    implements(ILineEditImpl)

    #---------------------------------------------------------------------------
    # ILineEditImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
