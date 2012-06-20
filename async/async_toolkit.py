#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.core.factory import EnamlFactory
from enaml.core.toolkit import Toolkit


class Constructor(EnamlFactory):
    """ An EnamlFactory subclass; instances of which are used to 
    populate a toolkit.

    """
    def __init__(self, shell_loader):
        """ Initialize a constructor instance.

        Parameters
        ----------
        shell_loader : Callable
            A callable object which returns the shell class to use
            for the widget.

        abstract_loader : Callable, optional
            A callable object which returns the abstract implementation
            class to use for the widget. If None, then it's assumed that
            the shell object has no abstract implementation.

        """
        super(Constructor, self).__init__()
        self.shell_loader = shell_loader

    def build(self, identifiers, toolkit):
        """ An abstractmethod implementation that builds an Enaml
        component using the classes returned from the provided
        loaders.

        """
        # This default constructor implementation simply ignores
        # the identifiers and toolkit, since they are no longer 
        # needed at the point when this method is called.
        shell_cls = self.shell_loader()
        shell_obj = shell_cls()
        return shell_obj


def window_loader():
    from components.window import Window
    return Window


items = {
    'Window': Constructor(window_loader)
}


async_toolkit = Toolkit(items)

from enaml.core.operators import OPERATORS

async_toolkit.update(OPERATORS)



