#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from base64 import b64encode, b64decode
from abstract_image import AbstractImage

class ImageFromFile(AbstractImage):
    """ A subclass of AbstractImage that allows the user to read in an image
    from a file.

    """
    def __init__(self, filename_or_data):
        """ Read the file and store its contents. If a filename is given, that
        file is read and its contents are stored as raw image data. If the
        argument is not a valid filename, then it is interpreted as a string
        of raw image data.

        """
        try:
            data = open(filename_or_data, 'rb').read()
            self._data = data
        except:
            self._data = filename_or_data
        
    def as_dict(self):
        """ Return the image as a JSON-serializable dict

        """
        image_dict = {
            'data' : b64encode(self._data),
            'format' : 'auto',
            'size' : (-1, -1)
        }
        return image_dict

    @staticmethod
    def from_dict(image_dict):
        """ Receive a JSON representation of an image and convert it into the
        appropriate Python object

        """
        data = b64decode(image_dict['data'])
        return ImageFromFile(data)

        
        
