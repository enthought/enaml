#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import os

class Image(object):
    """ An image
    
    """
    def __init__(self, data):
        """ Initialize an Image.

        """
        self._data = data

    def data(self):
        """ Return the data of the image

        """
        return self._data

    #--------------------------------------------------------------------------
    # Static methods
    #--------------------------------------------------------------------------
    @staticmethod
    def from_file(file_path):
        """ Read in the image data from a file.

        """
        if os.path.exists(file_path):
            data = open(file_path, 'rb').read()
            return Image(data)
        else:
            raise IOError("'%s' does not exist" % file_path)
