from .wx_component import WXComponent

from ..container import AbstractTkContainer


class WXContainer(WXComponent, AbstractTkContainer):
    """ A wxPython implementation of Container.

    WXContainer is usually to be used as a base class for other container
    widgets. However, it may also be used directly as an undecorated container
    for widgets for layout purposes.

    """

    # The WXComponent implementation is enough.
    pass
