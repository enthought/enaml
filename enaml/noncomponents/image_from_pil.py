#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from base64 import b64encode, b64decode
from StringIO import StringIO
from PIL import Image
from abstract_image import AbstractImage

class ImageFromPIL(AbstractImage):
    """ A subclass of AbstractImage that allows the user to read in an image
    from a numpy array.

    """
    def __init__(self, pil_image):
        """ Store the image

        """
        self._image = pil_image

    def as_dict(self):
        """ Return the image as a JSON-serializable dict

        """
        # XXX is there a better way to retrieve the data from a PIL image
        # than saving it to a string buffer?
        output = StringIO()
        self._image.save(output, format=self._image.format)
        contents = output.getvalue()
        output.close()

        image_dict = {
            'data' : b64encode(contents),
            'format' : self._image.format,
            'size' : self._image.size
        }
        return image_dict

    @staticmethod
    def from_dict(image_dict):
        """ Receive a JSON representation of an image and convert it into the
        appropriate Python object

        """
        dat = b64decode(image_dict['data'])
        image = Image.open(StringIO(dat))
        return ImageFromPIL(image)
