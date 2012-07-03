#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import os

class Icon(object):
    """ An icon
    
    """
    def __init__(self, data):
        """ Initialize an Icon.

        """
        self._data = data

    def data(self):
        """ Return the data of the icon

        """
        return self._data

    #--------------------------------------------------------------------------
    # Static methods
    #--------------------------------------------------------------------------
    @staticmethod
    def from_file(file_path):
        """ Read in the icon data from a file.

        """
        if os.path.exists(file_path):
            data = open(file_path, 'rb').read()
            return Icon(data)
        else:
            raise IOError("'%s' does not exist" % file_path)
