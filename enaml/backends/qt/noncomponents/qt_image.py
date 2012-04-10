#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

from ..qt.QtGui import QImage, QPixmap

from ....noncomponents.abstract_image import AbstractTkImage


class QtImage(AbstractTkImage):
    """ A Qt4 implementation of AbstractTkImage.
    
    """
    def __init__(self, qimage=None):
        """ Initialize a QtImage.

        Parameters
        ----------
        qimage : QImage instance or None, optional
            A QImage instance which holds the data. If None is passed, 
            then an empty QImage will be created.

        """
        if qimage is None:
            qimage = QImage()
        self._qimage = qimage
    
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
        # Shuffle the bytearray to match Qt's wonky ARGB format
        qt_array = bytearray(len(data))
        if sys.byteorder == 'little':
            r, g, b, a = (2, 1, 0, 3)
        else:
            r, g, b, a = (1, 2, 3, 0)
        qt_array[r::4] = data[0::4]
        qt_array[g::4] = data[1::4]
        qt_array[b::4] = data[2::4]
        qt_array[a::4] = data[3::4]

        w, h = size
        img_data = str(qt_array)
        qimg = QImage(img_data, w, h, QImage.Format_ARGB32)
        # Add a strong reference to the data so it doesn't get pulled out from
        # under the QImage object.
        qimg._data_keepalive_ptr = img_data
        return cls(qimg)

    @classmethod
    def from_file(cls, path, format=''):
        """ Read in the image data from a file.

        Parameters
        ----------
        path : string
            The path to the image file on disk.

        format : string or None, optional
            The image format of the data in the file. If not given,
            then the image format will be determined automatically
            if possible.
        
        Returns
        -------
        results : AbstractTkImage
            An appropriate image instance.

        """
        return cls(QImage(path, format))

    @property
    def size(self):
        """ The size of the image as a (width, height) tuple.
        
        Returns
        -------
        result : (width, height)
            The width, height size tuple of the image.

        """
        size = self._qimage.size()
        return (size.width(), size.height())
    
    def data(self):
        """ Returns the data for the image as a bytearray of RGBA bytes.
        
        Returns
        -------
        results : bytearray
            A bytearray of the image data in RGBA32 format.

        """
        qimg = self._qimage
        if qimg.format() != QImage.Format_ARGB32:
            qimg = qimg.convertToFormat(QImage.Format_ARGB32)

        # If bits() is None, then the image is invalid.
        buf = qimg.bits()
        if buf is None:
            return bytearray()

        # Qt's ARGB data format stores data as 0xAARRGGBB. On a little 
        # endian machine, the buffer of bytes will be ordered BBGGRRAA.
        out = bytearray(len(buf))
        if sys.byteorder == 'little':
            r, g, b, a = (2, 1, 0, 3)
        else:
            r, g, b, a = (1, 2, 3, 0)
        out[0::4] = buf[r::4]
        out[1::4] = buf[g::4]
        out[2::4] = buf[b::4]
        out[3::4] = buf[a::4]
        return out

    def scale(self, size):
        """ Returns a new version of this image scaled to the given size.
        
        Parameters
        ----------
        size : (width, height)
            The size of the scaled image.
        
        Returns
        -------
        results : AbstractTkImage
            A new image of the proper scaled size.
            
        """
        return QtImage(self._qimage.scaled(*size))

    #--------------------------------------------------------------------------
    # Toolkit Specific
    #--------------------------------------------------------------------------
    def as_QImage(self):
        """ Returns the internal QImage instance.

        """
        return self._qimage

    def as_QPixmap(self):
        """ Returns a QPixmap generated from the underlying QImage.
        
        This is provided as a convenience for qt backend components 
        which require a QPixmap rather than a QImage.
        
        """
        return QPixmap.fromImage(self._qimage)

