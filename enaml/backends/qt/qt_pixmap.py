#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from enaml.widgets.qt.qt import QtGui, QtCore

from ...components.abstract_pixmap import AbstractTkPixmap

# mapping Qt image formats to Enaml image format strings
format_map = {
    'RGB': QtGui.QImage.Format_RGB32,
    'ARGB': QtGui.QImage.Format_ARGB32,
    'aRGB': QtGui.QImage.Format_ARGB32_Premultiplied,
}
map_format = dict((value, key) for key, value in format_map.items())


class QtPixmap(AbstractTkPixmap):
    """ A raster image suitable for use within the UI
    
    This is implemented using a Qt QImage to hold the data for the image.  This
    QImage is public, and can be accessed via the qimage attribute of the class.
    The qpixmap property constructs a QPixmap from the qbitmap for situations
    where that is more appropriate.
    
    Arguments
    ---------
    qimage : QImage instance or None
        This is a QImage instance which holds the data.  If None is passed, then
        an empty QImage will be created.
    
    """
    
    def __init__(self, qimage=None):
        if qimage is None:
            qimage = QtGui.QImage()
        self.qimage = qimage
    
    @property
    def size(self):
        """ The size of the image.
        
        This is a tuple (width, height).
        
        """
        return self.qimage.size()
    
    @property
    def data(self):
        """ The underlying data for the image.
        
        This is a live buffer holding the underlying data with memory layed out
        as specified in the format property.
        
        """
        return self.qimage.bits()
    
    @property
    def format(self):
        """ The format of the image.
        
        This is a string which is one of the following:
            
            RGB - 24-bit RGB image
            ARGB - 32-bit RGB image with alpha before RGB
            aRGB - 32-bit RGB image with alpha premultiplied and before RGB

        """
        return map_format[self.qimage.format()]

    def scale(self, size):
        """ Create a version of this pixmap scaled to the given size.
        
        Arguments
        ---------
        
        size : tuple of width, height
            The size of the scaled image.
        
        """
        return QtPixmap(self.qimage.scaled(*size))
 
        
    #------------------------------------------------------------------------
    # Export to other formats
    #------------------------------------------------------------------------   

    def to_array(self):
        """ Extract the data from the pixmap into a numpy array
        
        This returns a structured array with an appropriate dtype for the
        format of the data.  Where possible this attempts to provide a view
        into the underlying data.
        
        """
        return super(QtPixamp, self).to_array()
            
    @property
    def qpixmap(self):
        """ A Qt QPixmap instance generated from the underlying QImage
        
        This is provided as a convenience for qt backend components which need
        a Qt Pixmap rather than a QImage.
        
        """
        return QtGui.QPixmap.fromImage(self.qimage)
    
    #------------------------------------------------------------------------
    # Constructors
    #------------------------------------------------------------------------
    
    @classmethod
    def from_file(cls, path):
        """ Read in the image data from a file
        
        This uses the Qt QImage constructor to infer the type of image being
        loaded.
        
        """
        qimage = QtGui.QImage(path)
        return cls(qimage)
 
    @classmethod
    def from_QPixmap(cls, qpixmap):
        qimage = qpixmap.toImage()
        image = cls(qimage)
        return image
