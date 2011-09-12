from traits.api import implements

from .qt_group import QtGroup

from ..vgroup import IVGroupImpl


class QtVGroup(QtGroup):
    """ A PySide implementation of IVGroup.

    This is a convienence subclass of QtGroup which restricts the 
    layout direction to vertical.

    See Also
    --------
    IVGroup
    
    """ 
    implements(IVGroupImpl)

    #---------------------------------------------------------------------------
    # IVGroupImpl interface
    #---------------------------------------------------------------------------
    
    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
