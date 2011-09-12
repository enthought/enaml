from traits.api import implements

from .qt_container import QtContainer

from ..group import IGroupImpl

from ...enums import Direction


class QtGroup(QtContainer):
    """ A PySide implementation of IGroup.
    
    See Also
    --------
    IGroup

    """
    implements(IGroupImpl)

    #---------------------------------------------------------------------------
    # IGroupImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
