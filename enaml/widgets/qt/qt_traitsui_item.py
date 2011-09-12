from traits.api import implements

from .qt_control import QtControl

from ..traitsui_item import ITraitsUIItemImpl


class QtTraitsUIItem(QtControl):
    """ A PySide implementation of TraitsUIItem.

    The traits ui item allows the embedding of a traits ui window in 
    an Enaml application.

    See Also
    --------
    TraitsUIItem

    """
    implements(ITraitsUIItemImpl)
    
    #---------------------------------------------------------------------------
    # ITraitsUIItemImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
