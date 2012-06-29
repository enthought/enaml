#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import os

from traits.api import (
    Bool, Enum, List, Unicode, Property, cached_property
)

from .dialog import Dialog

_FDIALOG_PROXY_ATTRS = ['mode', 'multi_select', 'directory', 'filename',
                        'path', 'paths', 'filters', 'selected_filter']

class FileDialog(Dialog):
    """ A dialog widget that allows the user to open/save files.

    """
    #: The mode of the dialog: 'open' or 'save'
    mode = Enum('open', 'save')

    #: Whether to allow selecting multiple files in 'open' mode. 
    multi_select = Bool(False)

    #: The current directory of the file dialog.
    directory = Unicode(os.path.abspath(os.path.curdir))

    #: The file selected in the dialog.
    filename = Unicode('')

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
   
    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(FileDialog, self).bind()
        self.default_send(*_FDIALOG_PROXY_ATTRS)

    def initial_attrs(self):
        """ Return the attr initialization dict for a window.

        """
        super_attrs = super(FileDialog, self).initial_attrs()
        get = getattr
        attrs = dict((attr, get(self, attr)) for attr in _FDIALOG_PROXY_ATTRS)
        super_attrs.update(attrs)
        return super_attrs

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_directory(self, ctxt):
        """ Message handler for set_directory

        """
        self.directory = ctxt['directory']
        return True

    def receive_set_filename(self, ctxt):
        """ Message handler for set_filename

        """
        self.filename = ctxt['filename']
        return True

    def receive_set_paths(self, ctxt):
        """ Message handler for set_paths

        """
        self._paths = ctxt['paths']
        return True

    def receive_set_selected_filter(self, ctxt):
        """ Message handler for set_selected_filter

        """
        self.selected_filter = ctxt['filter']
        return True
