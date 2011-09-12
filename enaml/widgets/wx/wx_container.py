from traits.api import implements

from .wx_component import WXComponent

from ..container import IContainerImpl


class WXContainer(WXComponent):
    """ A wxPython implementation of Container.

    The WXContainer class serves as a base class for other container
    widgets. It is not meant to be used directly.

    See Also
    --------
    Container

    """
    implements(IContainerImpl)

    #---------------------------------------------------------------------------
    # IContainerImpl interface
    #---------------------------------------------------------------------------
    
    # The IContainerImpl interface is empty

