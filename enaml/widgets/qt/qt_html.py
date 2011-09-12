from traits.api import implements

from .qt_control import QtControl

from ..html import IHtmlImpl


class QtHtml(QtControl):
    """ A PySide implementation of IHtml.

    See Also
    --------
    IHtml
    
    """
    implements(IHtmlImpl)

    #---------------------------------------------------------------------------
    # IHtmlImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
