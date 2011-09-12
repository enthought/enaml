from traits.api import implements

from .qt_control import QtControl

from ..spin_box import ISpinBoxImpl


class QtSpinBox(QtControl):
    """ A PySide implementation of SpinBox.

    See Also
    --------
    SpinBox

    """
    implements(ISpinBoxImpl)
    
    #---------------------------------------------------------------------------
    # ISpinBoxImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
