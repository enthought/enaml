#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abstract_image import AbstractImage

class ImageFromArray(AbstractImage):
    """ A subclass of AbstractImage that allows the user to read in an image
    from a numpy array.

    """
    def __init__(self, array, img_format):
        """ Store the array as the image data. img_format can be 'indexed8' or
        or 'rgba32' (case insensitive). The array can either be two or three
        dimensional.

        """
        self._data = array

        # if the array has more than two dimensions, only use the first two
        # for the size of the image
        if array.ndim > 2:
            self._size = (array.shape[0], array.shape[1])
        else:
            self._size = array.shape

        img_format = img_format.lower()
        if img_format not in ['indexed8', 'rgba32']:
            raise Exception("A value of '%s' was specified for the image format. "
            "The value must be either 'indexed8' or 'rgba32' (case-insensitive)"
                % img_format)
        self._format = img_format

    def as_dict(self):
        """ Return the image as a JSON-serializable dict

        """
        img_dict = {
            'data' : self._data.astype('uint8'),
            'format' : self._format,
            'size' : self._size
        }
        return img_dict

    @staticmethod
    def from_dict(image_dict):
        """ Receive a JSON representation of an image and convert it into the
        appropriate Python object

        """
        data = image_dict['data']
        img_format = image_dict['format']
        return ImageFromArray(data, img_format)
