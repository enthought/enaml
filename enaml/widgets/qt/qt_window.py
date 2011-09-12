from traits.api import implements

from .qt_component import QtComponent

from ..window import IWindowImpl


class QtWindow(QtComponent):
    """ A PySide implementation of a Window.

    See Also
    --------
    Window

    """
    implements(IWindowImpl)

    #---------------------------------------------------------------------------
    # IWindowImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
