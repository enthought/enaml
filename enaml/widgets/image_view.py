#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool

from .constraints_widget import ConstraintsWidget


_IV_PROXY_ATTRS = [
    #'image', 
    'scale_to_fit', 'preserve_aspect_ratio', 'allow_upscaling'
]


class ImageView(ConstraintsWidget):
    """ A simple viewer for instances of AbstractTkImage.

    """
    #: A Pixmap instance containing the image to display.
    # image = Instance(AbstractTkImage)
    
    #: Whether or not to scale the image with the size of the component.
    scale_to_fit = Bool(True)
    
    #: Whether or not to preserve the aspect ratio if scaling the image.
    preserve_aspect_ratio = Bool(True)

    #: Whether to allow upscaling of an image if scale_to_fit is True.
    allow_upscaling = Bool(True)

    #: An image view hugs its width weakly by default.
    hug_width = 'weak'

    #: An image view hugs its height weakly by default.
    hug_height = 'weak'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(ImageView, self).bind()
        self.default_send(*_IV_PROXY_ATTRS)

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(ImageView, self).initial_attrs()
        attrs = dict((attr, getattr(self, attr)) for attr in _IV_PROXY_ATTRS)
        super_attrs.update(attrs)
        return super_attrs

