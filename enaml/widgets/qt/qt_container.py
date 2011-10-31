from .qt_component import QtComponent

from ..container import AbstractTkContainer


class QtContainer(QtComponent, AbstractTkContainer):
    """ A Qt4 implementation of Container.

    QtContainer is usually to be used as a base class for other container
    widgets. However, it may also be used directly as an undecorated container
    for widgets for layout purposes.

    """

    # The QtComponent implementation is enough.
    # FIXME: should we move the QResizingFrame from QtComponent to here?
    pass
