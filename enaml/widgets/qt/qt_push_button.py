from traits.api import implements

from .qt_control import QtControl

from ..push_button import IPushButtonImpl


class QtPushButton(QtControl):
    """ A PySide implementation of PushButton.

    See Also
    --------
    PushButton

    """
    implements(IPushButtonImpl)

    #---------------------------------------------------------------------------
    # IPushButtonImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
