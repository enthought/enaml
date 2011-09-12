from traits.api import implements

from .qt_toggle_control import QtToggleControl

from ..check_box import ICheckBoxImpl


class QtCheckBox(QtToggleControl):
    """ A PySide implementation of CheckBox.

    See Also
    --------
    CheckBox

    """
    implements(ICheckBoxImpl)

    #---------------------------------------------------------------------------
    # ICheckBoxImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
