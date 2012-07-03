#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QPixmap, QIcon
from .qt.QtCore import QByteArray

class QtIcon(object):
    """ A Qt implementation of an icon
    
    """
    def __init__(self, data):
        """ Initialize a QtIcon.

        """        
        data_arr = QByteArray(data)
        self._pixmap = QPixmap()
        self._pixmap.loadFromData(data_arr)

        self._icon = QIcon(self._pixmap)

    def as_QPixmap(self):
        """ Return the icon as a QPixmap

        """
        return self._pixmap

    def as_QIcon(self):
        """ Return the icon as a QIcon

        """
        return self._icon
