#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from abc import ABCMeta, abstractmethod, abstractproperty


class AbstractImage(object):
    """ A raster image suitable for use within the UI
    """
    __metaclass__ = ABCMeta
    
    @abstractproperty
    def data(self):
        """ Return the underlying data.
        """
        return self.image.getdata()
    
    @abstractproperty
    def size(self):
        """ Return the size of the image.
        """
        return self.image.size
    
    @abstractmethod
    @classmethod
    def from_file(cls, path):
        image = Image.open(path)
        return cls(image)
