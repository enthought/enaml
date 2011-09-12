from traits.api import implements

from .qt_toggle_control import QtToggleControl

from ..radio_button import IRadioButtonImpl


class QtRadioButton(QtToggleControl):
    """ A PySide implementation of RadioButton.

    See Also
    --------
    RadioButton

    """
    implements(IRadioButtonImpl)

    #---------------------------------------------------------------------------
    # IRadioButtonImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
