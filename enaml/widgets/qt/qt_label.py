from traits.api import implements

from .qt_control import QtControl

from ..label import ILabelImpl


class QtLabel(QtControl):
    """ A PySide implementation of Label.
    
    See Also
    --------
    Label

    """
    implements(ILabelImpl)

 	#---------------------------------------------------------------------------
    # ILabelImpl interface 
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
