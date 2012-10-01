#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from numpy import ndarray, empty_like

from ..qt.QtGui import QImage
from .qt_abstract_image import QtAbstractImage

class QtArrayImage(QtAbstractImage):
    """ A Qt4 implementation of an Enaml ArrayImage.
    
    """
    #: the current image array
    _data = None
    
    #: the current image format
    _format = None
    
    #: a class variable mapping Enaml image formats to Qt4 image QImage.Formats
    _qt_formats = {
        'RGB': QImage.Format_RGB888,
        'RGBA': QImage.Format_ARGB32,
        'ARGB': QImage.Format_ARGB32,
    }
    
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, tree):
        """ Initializes the array data for the image.

        """
        super(QtArrayImage, self).create(tree)
        if 'data' in tree:
            data = self._pipe.decode_binary(tree['data'])
            size = tree['size']
            format = tree['format']
            self.set_image_array(data, format, size)
    
    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_image_array(self, content):
        """ Handle the 'set_image_array' action from the Enaml widget

        """
        data = self._pipe.decode_binary(content['data'])
        format = content['format']
        size = content['size']
        self.set_image_array(data, format, size)
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_image_array(self, data, format, size):
        """ Set the image array into a QImage, and load the QImage in a QPixmap
        
        """
        data = ndarray(shape=(len(data),), buffer=data, dtype='uint8')
        data.shape = (size[1], size[0], -1)
        if format == 'RGBA':
            data = self._shuffle_channels(data)
        height, width = size
        self._widget = QImage(data.data, height, width, self._qt_formats[format])
        self.refresh()
        self._data = data
    
    #--------------------------------------------------------------------------
    # Internal Methods
    #--------------------------------------------------------------------------
    def _shuffle_channels(self, data):
        """ Utility to transform RGBA to ARGB
        
        """
        new_data = empty_like(data)
        new_data[:,:,1:] = data[:,:,:-1]
        new_data[:,:,0] = data[:,:,-1]
        return new_data

