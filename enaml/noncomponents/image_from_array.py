#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abstract_image import AbstractImage
from base64 import b64encode, b64decode

_FORMATS = ['indexed8', 'rgba32', 'rgb32']

class ImageFromArray(AbstractImage):
    """ A subclass of AbstractImage that allows the user to read in an image
    from a bytearray.

    """
    def __init__(self, data, size, img_format, color_table=None):
        """ Store the array as the image data. img_format must be one of the
        values specified above (case-insensitive). color_table is an optional
        list of RGB tuples.

        """
        self._data = data
        self._size = size
        self._color_table = color_table

        img_format = img_format.lower()
        if img_format not in _FORMATS:
            raise Exception("A value of '%s' was specified for the image format. "
            "The value must one of the following: %s" % (img_format, _FORMATS))
        self._format = img_format

    def as_dict(self):
        """ Return the image as a JSON-serializable dict

        """
        img_dict = {
            'data' : b64encode(self._data),
            'format' : self._format,
            'size' : self._size,
            'color_table' : self._color_table
        }
        return img_dict

    @staticmethod
    def from_dict(image_dict):
        """ Receive a JSON representation of an image and convert it into the
        appropriate Python object

        """
        data = b64decode(image_dict['data'])
        size = image_dict['size']
        img_format = image_dict['format']
        color_table = image_dict['color_table']
        return ImageFromArray(data, size, img_format, color_table)
