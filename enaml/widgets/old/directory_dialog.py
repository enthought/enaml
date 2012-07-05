#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import os
from traits.api import Unicode
from .dialog import Dialog

_DIR_DIALOG_PROXY_ATTRS = ['directory']

class DirectoryDialog(Dialog):
    """ A dialog widget that allows the user to select directories.

    """
    #: The current directory of the dialog.
    directory = Unicode(os.path.abspath(os.path.curdir))

    #--------------------------------------------------------------------------
    # Parent Class Overrides 
    #--------------------------------------------------------------------------
    def add_subcomponent(self, component):
        """ An overriden parent class method which prevents subcomponents
        from being declared for a DirectoryDialog instance.

        """
        msg = "Cannot add subcomponents to a DirectoryDialog."
        raise ValueError(msg)

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(DirectoryDialog, self).bind()
        self.default_send(*_DIR_DIALOG_PROXY_ATTRS)

    def initial_attrs(self):
        """ Return the attr initialization dict for a window.

        """
        super_attrs = super(DirectoryDialog, self).initial_attrs()
        get = getattr
        attrs = dict((attr, get(self, attr)) for attr in _DIR_DIALOG_PROXY_ATTRS)
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
