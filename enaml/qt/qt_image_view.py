#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QLabel
from .qt.QtCore import Qt
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
       if self.pixmap() and self.hasScaledContents():
            size = resize_event.size()
            self.scale(size)

    def scale(self, size):
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

    def initialize(self, attrs):
       """ Initialize the attributes of the widget
       
       """
       super(QtImageView, self).initialize(attrs)
       self.set_allow_upscaling(attrs['allow_upscaling'])
       self.set_image(attrs['image'])
       self.set_preserve_aspect_ratio(attrs['preserve_aspect_ratio'])
       self.set_scale_to_fit(attrs['scale_to_fit'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_allow_upscaling(self, payload):
        """ Message handler for set_allow_upscaling

        """
        self.set_allow_upscaling(payload['allow_upscaling'])

    def on_message_set_image_data(self, payload):
        """ Message handler for set_image_data

        """
        self.set_image(payload['image'])

    def on_message_set_preserve_aspect_ratio(self, payload):
        """ Message handler for set_preserve_aspect_ratio

        """
        self.set_preserve_aspect_ratio(payload['preserve_aspect_ratio'])

    def on_message_set_scale_to_fit(self, payload):
        """ Message handler for set_scale_to_fit

        """
        self.set_scale_to_fit(payload['scale_to_fit'])
          
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_allow_upscaling(self, upscaling):
        """ Allow the widget to resize greater than itself when scaling

        """
        self.widget.allow_upscaling = upscaling

    def set_image(self, image):
        """ Set the image of the widget

        """
        self._image = QtImage(image)
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
