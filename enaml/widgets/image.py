#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
    
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
    def from_file(path):
        """ Read in the image data from a file.

        """
        data = open(path, 'rb').read()
        return Image(data)
