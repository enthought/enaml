#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

import wx

from ...components.abstract_pixmap import AbstractTkPixmap

class WXPixmap(AbstractTkPixmap):
    """ A raster image suitable for use within the UI
    
    This is implemeted using a wx Image instance to hold the data.  The
    constructor can optionally be passed an Image instance, otherwise it is
    initialized with a NullImage.
    
    """
    
    def __init__(self, wximage=None):
        if wximage is None:
            wximage = wx.NullImage
        self.wximage = wximage
    
    @property
    def data(self):
        """ The underlying data for the image.
        
        This returns either a single buffer of RGB data or a tuple of RGB buffer
        and alpha buffer.  These are live buffers and care needs to be taken
        that they are not garbage collected by Wx before any end users are done
        with them.
        
        """
        # XXX Should we just copy the data and not try to have live buffers?
        if self.wximage.HasAlpha():
            return (self.wximage.GetDataBuffer(), self.wximage.GetAlphaBuffer())
        else:
            return self.wximage.GetDataBuffer()
            
    @property
    def size(self):
        """ The size of the image.
        
        This is a tuple (width, height).
        
        """
        return (self.wximage.GetWidth(), self.wximage.GetHeight())
    
    @property
    def format(self):
        """ The format of the image.
        
        This is a string which is one of the following:
            
            RGB - 24-bit RGB image
            RGB,A - tuple of a 24-bit RGB image and the alpha channel as a separate buffer

        """
        if self.wximage.HasAlpha():
            return 'RGB,A'
        else:
            return 'RGB'
    
    def scale(self, size):
        """ Create a version of this pixmap scaled to the given size
        
        Arguments
        ---------
        
        size : tuple of width, height
            The size of the scaled image.
        
        """
        width, height = size
        return WXPixmap(self.wximage.Scale(width, height, wx.IMAGE_QUALITY_HIGH))

        
    #------------------------------------------------------------------------
    # Export to other formats
    #------------------------------------------------------------------------

    def to_array(self):
        """ Extract the data from the pixmap into a numpy array
        
        This returns a structured array with an appropriate dtype for the
        format of the data.  Where possible this attempts to provide a view
        into the underlying data.
        
        """
        from numpy import frombuffer
        data = self.data
        shape = self.size
        dtype = formats[self.format]
        return frombuffer(data, shape=shape, dtype=dtype)
    
    @property
    def wxbitmap(self):
        """ A wx Bitmap instance generated from the underlying wx Image
        
        This is provided as a convenience for wx backend components which need
        a wx Bitmap.
        
        """
        return wx.BitmapFromImage(self.wximage)

        
    #------------------------------------------------------------------------
    # Constructors
    #------------------------------------------------------------------------
    
    @classmethod
    def from_file(cls, path):
        """ Read in the image data from a file
        
        This uses the wx Image constructor to infer the type of image being
        loaded.
        
        """
        return cls(wx.Image(path))
