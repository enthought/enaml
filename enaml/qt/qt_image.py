#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QPixmap
from .qt.QtCore import QByteArray

class QtImage(object):
    """ A Qt implementation of an image
    
    """
    def __init__(self, data):
        """ Initialize a QtImage.

        """        
        data_arr = QByteArray(data)
        self._pixmap = QPixmap()
        self._pixmap.loadFromData(data_arr)

        self._image = self._pixmap.toImage()

    def as_QPixmap(self):
        """ Return the image as a QPixmap

        """
        return self._pixmap

    def as_QImage(self):
        """ Return the image as a QImage

        """
        return self._image
