#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty

from ..utils import abstractclassmethod


class AbstractTkImage(object):
    """ An abstract base class which represents a toolkit independent
    abstraction of a raster image.
    
    """
    __metaclass__ = ABCMeta

    @abstractclassmethod
    def from_data(cls, data, size):
        """ Construct an image from a bytearray of RGBA bytes.

        Parameters
        ----------
        data : bytearray
            A bytearray of the image data in RGBA32 format.

        size : (width, height)
            The width, height size tuple of the image.

        Returns
        -------
        results : AbstractTkImage
            An appropriate image instance.

        """
        raise NotImplementedError
    
    @abstractclassmethod
    def from_file(cls, path, format=''):
        """ Read in the image data from a file.

        Parameters
        ----------
        path : string
            The path to the image file on disk.

        format : string, optional
            The image format of the data in the file. If not given,
            then the image format will be determined automatically
            if possible.
        
        Returns
        -------
        results : AbstractTkImage
            An appropriate image instance.

        """
        raise NotImplementedError

    @abstractproperty
    def size(self):
        """ The size of the image as a (width, height) tuple.
        
        Returns
        -------
        result : (width, height)
            The width, height size tuple of the image.

        """
        raise NotImplementedError
    
    @abstractmethod
    def data(self):
        """ The data for the image as a bytearray of RGBA bytes.
        
        Returns
        -------
        results : bytearray
            A bytearray of the image data in RGBA32 format.

        """
        raise NotImplementedError

    @abstractmethod
    def scale(self, size):
        """ Create a new version of this image scaled to the given size.
        
        Parameters
        ----------
        size : (width, height)
            The size of the scaled image.
            
        Returns
        -------
        results : AbstractTkImage
            A new image of the proper scaled size.
            
        """
        raise NotImplementedError

