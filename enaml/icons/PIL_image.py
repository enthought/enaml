#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from PIL import Image

class PILImage(object):
    """ An image which uses the Python Imaging Library Image object to store data
    """
    
    def __init__(self, image):
        self.image = image
        self.image.convert("RGBA")
    
    @property
    def data(self):
        return self.image.getdata()
    
    @property
    def size(self):
        return self.image.size
    
    @classmethod
    def from_file(cls, path):
        image = Image.open(path)
        return cls(image)
