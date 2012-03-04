#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_control import QtControl

from ...components.image_view import AbstractTkImageView


class QtImageView(QtControl, AbstractTkImageView):
    """ A Qt4 implementation of ImageView.

    """
    #: The internal cached size hint which is used to determine whether
    #: of not a size hint updated event should be emitted when the image
    #: in the QLabel changes.
    _cached_size_hint = None

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QLabel control.

        """
        self.widget = QtGui.QLabel(parent)

    def initialize(self):
        """ Initializes the attributes on the underlying control.

        """
        super(QtImageView, self).initialize()
        shell = self.shell_obj
        self.set_image(shell.image)
        self.set_scale_to_fit(shell.scale_to_fit)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_image_changed(self, image):
        """ The change handler for the 'image' attribute on the shell 
        component.

        """
        self.set_image(image)
    
    def shell_scale_to_fit_changed(self, scale_to_fit):
        """ The change handler for the 'scale_to_fit' attribute on the 
        shell component.

        """
        self.set_scale_to_fit(scale_to_fit)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_image(self, image):
        """ Sets the image on the underlying QLabel.

        """
        self.widget.setPixmap(image.as_QPixmap())

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
    
    def set_scale_to_fit(self, scale_to_fit):        
        """ Sets whether or not the image scales with the underlying 
        control.

        """
        self.widget.setScaledContents(scale_to_fit)
        
        # See the comment in set_image(...) about the size hint update
        # notification. The same logic applies here.
        cached = self._cached_size_hint
        hint = self._cached_size_hint = self.size_hint()
        if cached != hint:
            self.shell_obj.size_hint_updated()

