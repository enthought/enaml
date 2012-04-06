#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty


class AbstractTkDockManager(object):
    """ 

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, *dock_panes):
        """ Initialize a DockManager instance.

        Parameters
        ----------
        *dock_panes
            The initial DockPane instances to use with the manager.

        """
        raise NotImplementedError

    @abstractproperty
    def main_window(self):
        """ A property which gets and sets the manager's internal 
        reference to the MainWindow instance. The internal reference
        should be stored weakly.

        """ 
        raise NotImplementedError

    @abstractmethod
    def add_pane(self, pane):
        """ Add a dock pane to the manager and hence the window.

        Parameters
        ----------
        pane : DockPane
            The DockPane instance to add to the manager. If the pane is
            already being managed, this method call is a no-op.
        
        """
        raise NotImplementedError
    
    @abstractmethod
    def remove_pane(self, pane):
        """ Remove a dock pane from the manager and hence the window.

        Parameters
        ----------
        pane : DockPane
            The DockPane instance to remove from the manager. If the
            pane is not being managed, this method call is a no-op.
        
        """
        raise NotImplementedError

    @abstractmethod
    def panes(self):
        """ Get the list of dock panes currently being managed.

        Returns
        -------
        result : list
            The list of DockPane instance being managed by this manager.
        
        """
        raise NotImplementedError

