from traits.api import implements

from .wx_component import WXComponent

from ..container import IContainerImpl


class WXContainer(WXComponent):
    """ A wxPython implementation of IContainer.

    The WXContainer class serves as a base class for other container
    widgets. It is not meant to be used directly.

    See Also
    --------
    IContainer

    """
    implements(IContainerImpl)

    #---------------------------------------------------------------------------
    # IContainerImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying widget (or sizer) for the container.

        """
        raise NotImplementedError

    def initialize_widget(self):
        """ Initialize the attributes of the container.

        """
        raise NotImplementedError

    def layout_child_widgets(self):
        """ Layout the children of the container.


        """
        raise NotImplementedError

