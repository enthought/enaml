#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod
import os

from traits.api import (
    Bool, Enum, List, Unicode, Instance, Property, cached_property
)

from .dialog import AbstractTkDialog, Dialog


class AbstractTkFileDialog(AbstractTkDialog):
    """ The abstract toolkit interface for a FileDialog.

    """
    @abstractmethod
    def shell_mode_changed(self, mode):
        """ Update the dialog for the given mode of behavior.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_multi_select_changed(self, multi_select):
        """ Update the dialog for the given multi select behavior.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_directory_changed(self, directory):
        """ Update the dialog with the new working directory.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_filename_changed(self, filename):
        """ Update the dialog with the new selected filename.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_filters_changed(self, filters):
        """ Update the dialog with the new filename filters.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_selected_filter_changed(self, selected_filter):
        """ Update the dialog with the new selected filter.

        """
        raise NotImplementedError


class FileDialog(Dialog):
    """ A dialog widget that allows the user to open/save files.

    """
    #: The mode of the dialog: 'open' or 'save'
    mode = Enum('open', 'save')

    #: Whether to allow selecting multiple files in 'open' mode. 
    multi_select = Bool(False)

    #: The current directory of the file dialog.
    directory = Unicode

    #: The file selected in the dialog.
    filename = Unicode

    #: A read-only property which returns the full path to the file,
    #: or the first file in the selection if multi_select is True.
    path = Property(Unicode, depends_on=['directory', 'filename'])

    #: A read-only property which returns a list of selected paths.
    paths = Property(List(Unicode), depends_on='_paths')

    #: The private internal storage for the 'paths' property. This is
    #: updated by the toolkit specific backends.
    _paths = List(Unicode)

    #: The string filters used to restrict the set of files.
    filters = List(Unicode)

    #: The selected filter from the list of filters.
    selected_filter = Enum(values='filters')

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkFileDialog)

    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_path(self):
        """ The property getter for the 'path' attribute.

        """
        return os.path.join(self.directory, self.filename)

    @cached_property
    def _get_paths(self):
        """ The property getter for the 'paths' attribute.

        """
        return self._paths
    
    #--------------------------------------------------------------------------
    # Parent Class Overrides 
    #--------------------------------------------------------------------------
    def add_subcomponent(self, component):
        """ An overriden parent class method which prevents subcomponents
        from being declared for a FileDialog instance.

        """
        msg = "Cannot add subcomponents to a FileDialog."
        raise ValueError(msg)

