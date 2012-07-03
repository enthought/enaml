#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from base64 import b64decode
from .qt.QtGui import QLabel
from .qt.QtCore import Qt, QSize
from .qt_constraints_widget import QtConstraintsWidget
from .qt_image import QtImage

class EnamlQtLabel(QLabel):
    """ An Enaml implementation of the QLabel. A subclass is needed because
    the resizeEvent must be overwritten to resize and preserve aspect ratio
    if necessary.

    """
    def __init__(self, parent):
       super(EnamlQtLabel, self).__init__(parent)
       self.preserve_aspect_ratio = True
       self.allow_upscaling = True
        
    def resizeEvent(self, resize_event):
       # The pixmap is initialized to None, causing the resizing to throw an
       # error, so we have to check that the pixmap exists before continuing
       # with the resize
       if self.pixmap():
            size = resize_event.size()
            if self.preserve_aspect_ratio:
               if self.allow_upscaling:
                  aspect_ratio = Qt.KeepAspectRatioByExpanding
               else:
                  aspect_ratio = Qt.KeepAspectRatio
            else:
                aspect_ratio = Qt.IgnoreAspectRatio

            pix = self.pixmap().scaled(size, aspect_ratio)
            self.setPixmap(pix)

class QtImageView(QtConstraintsWidget):
    """ A Qt implementation of an image view. Uses a QLabel to display the
    image.
   
    """
    def create(self):
       """ Create the underlying widget
      
       """
       self.widget = EnamlQtLabel(self.parent_widget)

    def initialize(self, init_attrs):
       """ Initialize the attributes of the widget
       
       """
       super(QtImageView, self).initialize(init_attrs)
       self.set_allow_upscaling(init_attrs.get('allow_upscaling', True))
       self.set_image_data(init_attrs.get('image_data', ''))
       self.set_preserve_aspect_ratio(init_attrs.get('preserve_aspect_ratio', True))
       self.set_scale_to_fit(init_attrs.get('scale_to_fit', True))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_allow_upscaling(self, ctxt):
        """ Message handler for set_allow_upscaling

        """
        upscaling = ctxt.get('allow_upscaling')
        if upscaling is not None:
            self.set_allow_upscaling(upscaling)

    def receive_set_image_data(self, ctxt):
        """ Message handler for set_image_data

        """
        image_data = ctxt.get('image')
        if image_data is not None:
            self.set_image_data(image_data)

    def receive_set_preserve_aspect_ratio(self, ctxt):
        """ Message handler for set_preserve_aspect_ratio

        """
        ratio = ctxt.get('preserve_aspect_ratio')
        if ratio is not None:
            self.set_preserve_aspect_ratio(ratio)

    def receive_set_scale_to_fit(self, ctxt):
        """ Message handler for set_scale_to_fit

        """
        scale = ctxt.get('scale_to_fit')
        if scale is not None:
            self.set_scale_to_fit(scale)

    def receive_scale(self, ctxt):
       """ Message hander for scale

       """
       size = ctxt.get('size')
       if size is not None:
          self.scale(size)
          
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_allow_upscaling(self, upscaling):
        """ Allow the widget to resize greater than itself when scaling

        """
        self.widget.allow_upscaling = upscaling

    def set_image_data(self, image_data):
        """ Set the image of the widget

        """
        dec_data = b64decode(image_data)
        self._image = QtImage(dec_data)
        self.widget.setPixmap(self._image.as_QPixmap())
    
    def set_preserve_aspect_ratio(self, ratio):
        """ Set whether or not to preserve aspect ratio

        """
        self.widget.preserve_aspect_ratio = ratio

    def set_scale_to_fit(self, scale):
        """ Set whether or not to allow the image to scale to fill available
        space.

        """
        self.widget.setScaledContents(scale)

    def scale(self, size):
       """ Scale the view's image to a given size

       """
       self.widget.resize(QSize(*size))
