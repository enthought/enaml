#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_control import QtControl

from ...components.image import AbstractTkImage


class QtImage(QtControl, AbstractTkImage):
    """ A Qt implementation of Image.

    """
    #: The internal cached size hint which is used to determine whether
    #: of not a size hint updated event should be emitted when the text
    #: in the label changes
    _cached_size_hint = None

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wx.StaticBitmap control.

        """
        self.widget = QtGui.QLabel(parent)

    def initialize(self):
        """ Initializes the attributes on the underlying control.

        """
        super(QtImage, self).initialize()
        self.set_pixmap(self.shell_obj.pixmap)
        self.set_scale_pixmap(self.shell_obj.scale_pixmap)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_pixmap_changed(self, pixmap):
        """ The change handler for the 'pixmap' attribute on the shell 
        component.

        """
        self.set_label(pixmap)

    def shell_img_width_changed(self, width):
        """ The change handler for the 'img_width' attribute on the shell 
        component.

        """
        pass

    def shell_img_height_changed(self, height):
        """ The change handler for the 'img_height' attribute on the shell 
        component.

        """
        pass
    
    def shell_scale_pixmap_changed(self, scale_pixmap):
        """ The change handler for the 'scale_image' attribute on the shell 
        component.

        """
        self.set_scale_pixmap(scale_pixmap)

    def set_pixmap(self, pixmap):
        """ Sets the pixmap on the underlying control.

        """
        qpixmap = pixmap.qpixmap
        self.widget.setPixmap(qpixmap)

        # Emit a size hint updated event if the size hint has actually
        # changed. This is an optimization so that a constraints update
        # only occurs when the size hint has actually changed. This 
        # logic must be implemented here so that the label has been
        # updated before the new size hint is computed. Placing this
        # logic on the shell object would not guarantee that the label
        # has been updated at the time the change handler is called.
        cached = self._cached_size_hint
        hint = self._cached_size_hint = self.size_hint()
        if cached != hint:
            self.shell_obj.size_hint_updated()
    
    def set_scale_pixmap(self, scale_pixmap):        
        """ Sets whether or not the pixmap scales with the underlying control.

        """
        self.widget.setScaledContents(scale_pixmap)
        self.shell_obj.size_hint_updated()
