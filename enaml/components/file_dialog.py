#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum, Int, Unicode

from .dialog import Dialog


class FileDialog(Dialog):
    """ A dialog widget that allows the user to open/save files.

    """
    #: The type of file dialog: open or save
    type = Enum("open", "save")

    # The default directory.
    default_directory = Unicode

    # The default filename.
    default_filename = Unicode

    # The default path (directory and filename) of the chosen file.  This is
    # only used when the *default_directory* and *default_filename* are not set
    # and is equivalent to setting both.
    default_path = Unicode

    # The directory containing the chosen file.
    directory = Unicode

    # The name of the chosen file.
    filename = Unicode

    # The path (directory and filename) of the chosen file.
    path = Unicode

    # The wildcard used to restrict the set of files.
    wildcard = Unicode

    # The index of the selected wildcard.
    wildcard_index = Int(0)

