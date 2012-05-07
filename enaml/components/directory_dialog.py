#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Unicode, Instance

from .dialog import AbstractTkDialog, Dialog


class AbstractTkDirectoryDialog(AbstractTkDialog):
    """ The abstract toolkit interface for a DirectoryDialog.

    """
    @abstractmethod
    def shell_directory_changed(self, directory):
        """ Update the dialog with the new working directory.

        """
        raise NotImplementedError


class DirectoryDialog(Dialog):
    """ A dialog widget that allows the user to select directories.

    """
    #: The current directory of the dialog.
    directory = Unicode

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkDirectoryDialog)

    #--------------------------------------------------------------------------
    # Parent Class Overrides 
    #--------------------------------------------------------------------------
    def add_subcomponent(self, component):
        """ An overriden parent class method which prevents subcomponents
        from being declared for a DirectoryDialog instance.

        """
        msg = "Cannot add subcomponents to a DirectoryDialog."
        raise ValueError(msg)

