from traits.api import implements

from .qt_group import QtGroup

from ..hgroup import IHGroupImpl


class QtHGroup(QtGroup):
    """ A PySide implementation of IHGroup.

    This is a convienence subclass of QtGroup which restricts the
    layout direction to horizontal.

    See Also
    --------
    IHGroup
    
    """ 
    implements(IHGroupImpl)

    #---------------------------------------------------------------------------
    # IHGroupImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
