#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from ....noncomponents.abstract_image import AbstractTkImage


FLAG_MAP = {
    'bmp': wx.BITMAP_TYPE_BMP,
    'gif': wx.BITMAP_TYPE_GIF,
    'jpg': wx.BITMAP_TYPE_JPEG,
    'jpeg': wx.BITMAP_TYPE_JPEG,
    'png': wx.BITMAP_TYPE_PNG,
    'pcx': wx.BITMAP_TYPE_PCX,
    'pnm': wx.BITMAP_TYPE_PNM,
    'tif': wx.BITMAP_TYPE_TIF,
    'tiff': wx.BITMAP_TYPE_TIF,
    'tga': wx.BITMAP_TYPE_TGA,
    'xpm': wx.BITMAP_TYPE_XPM,
    'ico': wx.BITMAP_TYPE_ICO,
    'cur': wx.BITMAP_TYPE_CUR,
    'ani': wx.BITMAP_TYPE_ANI,
    '': wx.BITMAP_TYPE_ANY,
}


class WXImage(AbstractTkImage):
    """ A Wx implementation of AbstractTkImage.
    
    """
    def __init__(self, wximage=None):
        """ Initialize a WXImage.

        Parameters
        ----------
        wximage : wx.Image instance or None, optional
            A wx.Image instance which holds the data. If None is passed, 
            then the wx.NullImage will be used.

        """
        if wximage is None:
            wximage = wx.NullImage
        self._wximage = wximage
    
    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    @classmethod
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
        w, h = size

        # Split the array into color and alpha to satisfy WX
        rgb_array = bytearray(w*h*3)
        alpha_array = bytearray(w*h)
        
        rgb_array[0::3] = data[0::4]
        rgb_array[1::3] = data[1::4]
        rgb_array[2::3] = data[2::4]
        alpha_array[:] = data[3::4]

        return cls(wx.ImageFromDataWithAlpha(w, h, rgb_array, alpha_array))

    @classmethod
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
        flag = FLAG_MAP.get(format.lower(), wx.BITMAP_TYPE_ANY)
        return cls(wx.Image(path, flag))

    @property
    def size(self):
        """ The size of the image as a (width, height) tuple.
        
        Returns
        -------
        result : (width, height)
            The width, height size tuple of the image.

        """
        img = self._wximage
        return (img.GetWidth(), img.GetHeight())

    def data(self):
        """ The data for the image as a bytearray of RGBA bytes.
        
        Returns
        -------
        results : bytearray
            A bytearray of the image data in RGBA32 format.

        """
        wximg = self._wximage
        width, height = wximg.GetWidth(), wximg.GetHeight()
        buf = wximg.GetDataBuffer()
        out = bytearray(width * height * 4)
        out[0::4] = buf[0::3]
        out[1::4] = buf[1::3]
        out[2::4] = buf[2::3]   
        if wximg.HasAlpha():
            out[3::4] = wximg.GetAlphaBuffer()[:]
        else:
            out[3::4] = '\xff' * (width * height)
        return out

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
        width, height = size
        new_img = self._wximage.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        return WXImage(new_img)
        
    #--------------------------------------------------------------------------
    # Toolkit Specific
    #--------------------------------------------------------------------------
    def as_wxImage(self):
        """ Returns the internal wx.Image instance.

        """
        return self._wximage

    def as_wxBitmap(self):
        """ Returns a wx.Bitmap generated from the underlying wx.Image.
        
        This is provided as a convenience for wx backend components 
        which require a wx.Bitmap rather than a wx.Image.
        
        """
        return wx.BitmapFromImage(self._wximage)

