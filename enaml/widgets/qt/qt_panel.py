from traits.api import implements

from .qt_component import QtComponent

from ..panel import IPanelImpl


class QtPanel(QtComponent):
    """ A PySide implementation of Panel.

    See Also
    --------
    Panel

    """
    implements(IPanelImpl)

    #---------------------------------------------------------------------------
    # IPanelImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
