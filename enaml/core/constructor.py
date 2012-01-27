#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .factory import EnamlFactory


class Constructor(EnamlFactory):
    """ An EnamlFactory subclass; instances of which are used to 
    populate a toolkit.

    """
    def __init__(self, shell_loader, abstract_loader=None):
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
        self.abstract_loader = abstract_loader

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
        abstract_loader = self.abstract_loader
        if abstract_loader is not None:
            abstract_obj = abstract_loader()()
            shell_obj.abstract_obj = abstract_obj
            abstract_obj.shell_obj = shell_obj
        return shell_obj

    def clone(self, shell_loader=None, abstract_loader=None):
        """ Creates a clone of this constructor, optionally changing
        out one or both of the loaders.

        """
        if shell_loader is None:
            shell_loader = self.shell_loader
        if abstract_loader is None:
            abstract_loader = self.abstract_loader
        return Constructor(shell_loader, abstract_loader)

