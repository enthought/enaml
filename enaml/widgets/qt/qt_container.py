from traits.api import implements

from .qt_component import QtComponent

from ..container import IContainerImpl


class QtContainer(QtComponent):
    """ A Qt implementation of Container.

    The QtContainer class serves as a base class for other container
    widgets. It is not meant to be used directly.

    See Also
    --------
    Container

    """
    implements(IContainerImpl)

    #---------------------------------------------------------------------------
    # IContainerImpl interface
    #---------------------------------------------------------------------------
    def create_style_handler(self):
        """ Creates and sets the window style handler.

        """
        pass
    
    def initialize_style(self):
        """ Initializes the style for the window.

        """
        pass
