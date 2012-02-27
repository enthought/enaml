#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from abc import ABCMeta, abstractmethod, abstractproperty

class AbstractTkPixmap(object):
    """ An abstract toolkit raster image
    
    """
    __metaclass__ = ABCMeta
    
    @abstractproperty
    def size(self):
        """ The size of the image.
        
        This is a tuple (width, height).
        
        """
        raise NotImplementedError
    
    @abstractproperty
    def data(self):
        """ The underlying data for the image.
        
        Where possible this attempts to return a live buffer into the underlying
        data with memory layed out as specified in the format property.
        
        """
        # XXX Should we just copy the data and not try to have live buffers?
        raise NotImplementedError
    
    @abstractproperty
    def format(self):
        """ The format of the image.
        
        This is a string which is one of the following:
            
            RGB - 24-bit RGB image
            RGBA - 32-bit RGB image with alpha after RGB
            ARGB - 32-bit RGB image with alpha before RGB
            RGBa - 32-bit RGB image with alpha premultiplied and after RGB
            aRGB - 32-bit RGB image with alpha premultiplied and before RGB
            RGB,A - tuple of a 24-bit RGB image and the alpha channel as a separate buffer

        """
        raise NotImplementedError
    
    @abstractmethod
    def scale(self, size):
        """ Create a version of this pixmap scaled to the given size
        
        Arguments
        ---------
        
        size : tuple of width, height
            The size of the scaled image.
        
        """
        raise NotImplementedError

    #------------------------------------------------------------------------
    # Export to other formats
    #------------------------------------------------------------------------
    
    @abstractmethod
    def to_array(self):
        """ Extract the data from the pixmap into a numpy array
        
        This returns a structured array with an appropriate dtype for the
        format of the data.  Where possible this attempts to provide a view
        into the underlying data.
        
        """
        from numpy import frombuffer
        from .formats import formats
        data = self.data
        shape = self.size
        dtype = formats[self.format]
        return frombuffer(data, shape=shape, dtype=dtype)
    
    #------------------------------------------------------------------------
    # Constructors
    #------------------------------------------------------------------------
    
    @classmethod
    def from_file(cls, path):
        """ Read in the image data from a file
        
        This should attempt to infer the image type from file's data.
        
        """
        raise NotImplementedError
