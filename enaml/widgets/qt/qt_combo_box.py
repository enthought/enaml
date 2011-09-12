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
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
