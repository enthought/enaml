#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import namedtuple
from functools import wraps
from os import listdir
from os.path import abspath, isabs, normpath, join, isdir, pardir
import re

from enaml.core.item_model import AbstractListModel, ModelIndex, ALIGN_LEFT, ALIGN_VCENTER


# A named tuple which holds the relative path of an item in the 
# current working directory of the model, and whether or not that 
# item is a directory.
_FlatRecord = namedtuple('_FlatRecord', 'is_dir rel_path')


def _reset_model(func):
    """ A method decorator which will reset an abstract item model.

    """
    @wraps(func)
    def closure(self, *args, **kwargs):
        self.begin_reset_model()
        res = func(self, *args, **kwargs)
        self.end_reset_model()
        return res
    return closure


def _refresh_data(func):
    """ A method decorator which will trigger a refresh of all data in 
    a list model. This assumes that the data in the list model is in 
    the zero column.

    """
    @wraps(func)
    def closure(self, *args, **kwargs):
        parent = None
        top_left = self.index(0, 0, parent)
        bottom_right = self.index(self.row_count(parent) - 1, 0, parent)
        res = func(self, *args, **kwargs)
        self.notify_data_changed(top_left, bottom_right)
        return res
    return closure


class FlatFileSystemModel(AbstractListModel):
    """ A concrete list model implementation which navigates a mounted
    filesystem one directory at a time.

    """
    def __init__(
        self, directory='.', show_hidden=False, file_pattern=r'.*', 
        dir_icon=None, file_icon=None):
        """ Initialize a FlatFilesystemModel.

        Parameters
        ----------
        directory : string, optional
            The path to the working directory. Defaults to the current
            working directory.

        show_hidden : bool, optional
            Whether or not to show hidden files. Defaults to False.

        file_pattern : string, optional
            A regex pattern which will be compiled and matched against 
            the file names in a directory. Only files which match the 
            pattern will be accepted. Matching is performed in a case 
            insensitive fashion. The default pattern matches everything. 
            More controlled filtering may be obtained by overriding the 
            filter_dir and filter_file methods.

        dir_icon : Icon, optional
            An optional icon to display next to directory names.

        file_icon : Icon, optional
            An optional icon to display next to file name.

        """
        self._cwd = abspath(normpath(directory))
        self._show_hidden = show_hidden
        self._file_pattern = file_pattern
        self._file_pattern_rgx = re.compile(file_pattern, re.IGNORECASE)
        self._dir_icon = dir_icon
        self._file_icon = file_icon
        self._contents = []
        self._loadcwd()

    #--------------------------------------------------------------------------
    # AbstractListModel Implementation Methods
    #--------------------------------------------------------------------------
    def row_count(self, parent):
        """ Returns the number of rows in the model, which is equal to 
        the number of items in the current directory.

        """
        if parent is not None:
            return 0
        return len(self._contents)

    def data(self, index):
        """ Returns the display data for the given row, which is the 
        relative path for that item in the current directory.

        """
        return self._contents[index.row].rel_path

    def alignment(self, index):
        """ Returns the alignment for the given row. By default, items
        align to the left and vertically centered.

        """
        return ALIGN_LEFT | ALIGN_VCENTER
    
    def decoration(self, index):
        """ Returns the appropriate file or directory icon for the 
        given index.

        """
        if self.isdir(index):
            return self._dir_icon
        return self._file_icon

    #--------------------------------------------------------------------------
    # Private Methods
    #--------------------------------------------------------------------------
    def _loadcwd(self):
        """ Loads the contents of the current working directory.

        Parameters
        ----------
        directory : string
            The directory for which to retrieve items.

        Returns
        -------
        result : list of 2-tuples
            A list of 2-tuples of the form (bool, string) where the 
            boolean indicates whether the item is a directory and 
            the string is the relative path to the item.

        """
        contents = self._contents = []
        push = contents.append
        cwd = self._cwd
        filter_dir = self.filter_dir
        filter_file = self.filter_file
        rcd = _FlatRecord

        # The first item in a directory is always the relative path to
        # the parent directory. This allows for simple navigation 
        # through the filesystem. But we may want to update it in the
        # future to use something like a breadcrumbs widget.
        push(rcd(True, pardir))
        for item in listdir(cwd):
            if isdir(join(cwd, item)):
                if filter_dir(item):
                    push(rcd(True, item))
            else:
                if filter_file(item):
                    push(rcd(False, item))

    #--------------------------------------------------------------------------
    # Public Properties
    #--------------------------------------------------------------------------
    def _get_show_hidden(self):
        """ Returns whether or not hidden directories and files are
        shown.

        """
        return self._show_hidden

    @_reset_model
    def _set_show_hidden(self, show):
        """ Set whether or not hidden directories and files are shown.

        """
        self._show_hidden = show
        self._loadcwd()

    show_hidden = property(_get_show_hidden, _set_show_hidden)

    def _get_file_pattern(self):
        """ Return the current file pattern in use by the model.

        """
        return self._file_pattern

    @_reset_model
    def _set_file_pattern(self, file_pattern):
        """ Set the pattern to be used by the model.

        """
        self._file_pattern = file_pattern
        self._file_pattern_rgx = re.compile(file_pattern, re.IGNORECASE)
        self._loadcwd()

    file_pattern = property(_get_file_pattern, _set_file_pattern)

    def _get_dir_icon(self):
        """ Return the directory icon in use by the model.

        """
        return self._dir_icon

    @_refresh_data
    def _set_dir_icon(self, icon):
        """ Set the directory icon in use by the model.

        """
        self._dir_icon = icon

    dir_icon = property(_get_dir_icon, _set_dir_icon)

    def _get_file_icon(self):
        """ Return the file icon in use by the model.

        """
        return self._file_icon

    @_refresh_data
    def _set_file_icon(self, icon):
        """ Set the file icon in use by the model.

        """
        self._file_icon = icon

    file_icon = property(_get_file_icon, _set_file_icon)

    #--------------------------------------------------------------------------
    # Public Methods
    #--------------------------------------------------------------------------
    def getcwd(self):
        """ Returns the current working directory.

        """
        return self._cwd

    @_reset_model
    def chdir(self, directory):
        """ Sets the current working directory and refresh the model.

        Parameters
        ----------
        directory : string or ModelIndex
            A relative or absolute path to a directory, or a model index
            pointing to a directory in the current working directory.

        """
        if isinstance(directory, ModelIndex):
            directory = self._contents[directory.row].rel_path
        if not isabs(directory):
            directory = join(self._cwd, directory)
        self._cwd = abspath(normpath(directory))
        self._loadcwd()

    def isdir(self, index):
        """ Returns whether or not the item at the given index is a 
        directory.

        Calling os.path.isdir is an expensive system call, which is
        therefore only done once when loading a new directory. Using
        this method when needing to query for directory status will
        save time.

        Parameters
        ----------
        index : ModelIndex
            The model index for the associated item.

        Returns
        -------
        result : bool
            True if the model index points to a directory. False 
            otherwise.

        """
        return self._contents[index.row].is_dir

    def abspath(self, index):
        """ Return the absolute path to the item at the given index.

        Parameters
        ----------
        index : ModelIndex
            The model index for the associated item.

        Returns
        -------
        result : string
            The absolute path to the item pointed to by the index.

        """
        return join(self._cwd, self._contents[index.row].rel_path)

    def filter_dir(self, directory):
        """ Returns whether or not to include the given directory in the 
        results for the current directory.

        The default implementation filters based on whether or not the
        directory is hidden (according the model flag).

        Parameters
        ----------
        directory : string
            The directory which should be tested for inclusion.

        Returns
        -------
        result : bool
            True if the directory should be included, False otherwise.

        """
        if not self._show_hidden and directory.startswith('.'):
            return False
        return True

    def filter_file(self, item):
        """ Returns whether or not to include the given item in the 
        results for the current directory.

        The default implementation filters based on whether or not the
        item is hidden (according the model flag) and whether or not it 
        matches the provided pattern.

        Parameters
        ----------
        items : string
            The items which should be tested for inclusion.

        Returns
        -------
        result : bool
            True if the item should be included, False otherwise.

        """
        if not self._show_hidden and item.startswith('.'):
            return False
        return bool(self._file_pattern_rgx.match(item))

