#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys
from base64 import b64decode
from .qt.QtGui import QPixmap, QIcon, QImage, qRgb
from .qt.QtCore import QByteArray

_QT_IMAGE_FORMAT = {
    'rgb32': QImage.Format_ARGB32,
    'rgba32': QImage.Format_ARGB32,
    'indexed8': QImage.Format_Indexed8
}

class QtImage(object):
    """ A Qt implementation of an image
    
    """
    def __init__(self, info):
        """ Initialize a QtImage. info is a dict containing the image data,
        image size, image format, and optionally, a color table

        """
        # These converters are necessary to shuffle around the channels in the data to
        # match Qt's format
        _FORMAT_CONVERTERS = {
            'rgb32': self.rgb_converter,
            'rgba32': self.rgba_converter
        }

        data = info['data']
        w, h = info['size']
        _format = info['format']
        color_table = info.get('color_table')

        if _format == 'raw_file':
            qt_data = QByteArray(b64decode(data))
            self._image = QImage()
            self._image.loadFromData(qt_data)
        else:
            qt_data = _FORMAT_CONVERTERS[_format](b64decode(data))
            self._image = QImage(str(qt_data), w, h, _QT_IMAGE_FORMAT[_format])
            if color_table:
                self._image.setColorTable([qRgb(*color) for color in color_table])

    def rgb_converter(self, data):
        """ Shuffle the RGB channels and add an alpha channel to conform with Qt
            XXX: Qt supports just an RGB format (no alpha), but there were issues
            with it so we just added an alpha channel filled with 255 and used the
            ARGB format.
        """
        if sys.byteorder == 'little':
            r, g, b, a = (2, 1, 0, 3)
        else:
            r, g, b, a = (1, 2, 3, 0)

        qt_data = bytearray(len(data))
        qt_data[r::4] = data[0::4]
        qt_data[g::4] = data[1::4]
        qt_data[b::4] = data[2::4]
        qt_data[a::4] = [255] * len(qt_data[a::4])

        return qt_data

    def rgba_converter(self, data):
        """ Shuffle the RGBA channels to conform with Qt

        """
        if sys.byteorder == 'little':
            r, g, b, a = (2, 1, 0, 3)
        else:
            r, g, b, a = (1, 2, 3, 0)
            
        qt_data = bytearray(len(data))
        qt_data[r::4] = data[0::4]
        qt_data[g::4] = data[1::4]
        qt_data[b::4] = data[2::4]
        qt_data[a::4] = data[3::4]

        return qt_data
    
    def as_QPixmap(self):
        """ Return the image as a QPixmap

        """
        return QPixmap.fromImage(self._image)

    def as_QIcon(self):
        """ Return the image as a QIcon

        """
        return QIcon(self._pixmap)
