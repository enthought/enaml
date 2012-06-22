#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from .qt.QtGui import QLabel
from .qt.QtCore import Qt
from .qt_control import QtControl

class EnamlQtLabel(QLabel):
    """ An Enaml implementation of the QLabel. A subclass is needed because
    the resizeEvent must be overwritten to resize and preserve aspect ratio
    if necessary.

    """
    def __init__(self, parent):
        self.preserve_aspect_ratio = False
        super(EnamlQtLabel, self).__init__(parent)
        
    def resizeEvent(self, resize_event):
       size = resize_event.size()
       if self.preserve_aspect_ratio:
           aspect_ratio = Qt.KeepAspectRatio
       else:
           aspect_ratio = Qt.IgnoreAspectRatio
           
       pix = self.pixmap().scaled(size, aspect_ratio)
       self.setPixmap(pix)

class QtImageView(QtControl):
    """ A Qt implementation of an image view. Uses a QLabel to display the
    image.

    """
    def create(self, parent):
        """ Create the underlying widget

        """
        self.widget = EnamlQtLabel(parent)
        self.widget.show()

    def initialize(self, init_attrs):
        """ Initialize the attributes of the widget

        """
        self.set_allow_upscaling(init_attrs.get('allow_upscaling'))
        self.set_image(init_attrs.get('image'))
        self.set_preserve_aspect_ratio(init_attrs.get('preserve_aspect_ratio'))
        self.set_scale_to_fit(init_attrs.get('scale_to_fit'))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_allow_upscaling(self, ctxt):
        """ Message handler for set_allow_upscaling

        """
        upscaling = ctxt.get('value')
        if upscaling is not None:
            self.set_allow_upscaling(upscaling)

    def receive_set_image(self, ctxt):
        """ Message handler for set_image

        """
        image = ctxt.get('value')
        if image is not None:
            self.set_image(image)

    def receive_set_preserve_aspect_ratio(self, ctxt):
        """ Message handler for set_preserve_aspect_ratio

        """
        ratio = ctxt.get('value')
        if ratio is not None:
            self.set_preserve_aspect_ratio(ratio)

    def receive_set_scale_to_fit(self, ctxt):
        """ Message handler for set_scale_to_fit

        """
        scale = ctxt.get('value')
        if scale is not None:
            self.set_scale_to_fit(scale)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_allow_upscaling(self, upscaling):
        """ 

        """
        # XXX implementation and docstring?
        pass

    def set_image(self, image):
        """ Set the image of the widget

        """
        # XXX no way to handle images right now
        self.widget.setPixmap(image)

    def set_preserve_aspect_ratio(self, ratio):
        """ Set whether or not to preserve aspect ratio

        """
        self.widget.preserve_aspect_ratio = ratio

    def set_scale_to_fit(self, scale):
        """ Set whether or not to allow the image to scale to fill available
        space.

        """
        self.widget.setScaledContents(scale)
