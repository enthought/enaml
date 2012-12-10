#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Str

from .control import Control


class ImageView(Control):
    """ A widget which can display an Image with optional scaling.

    """
    #: The source url of the image to load.
    source = Str

    #: Whether or not to scale the image with the size of the component.
    scale_to_fit = Bool(False)

    #: Whether to allow upscaling of an image if scale_to_fit is True.
    allow_upscaling = Bool(True)

    #: Whether or not to preserve the aspect ratio if scaling the image.
    preserve_aspect_ratio = Bool(True)

    #: An image view hugs its width weakly by default.
    hug_width = 'weak'

    #: An image view hugs its height weakly by default.
    hug_height = 'weak'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the dict of creation attribute for the control.

        """
        snap = super(ImageView, self).snapshot()
        snap['source'] = self.source
        snap['scale_to_fit'] = self.scale_to_fit
        snap['allow_upscaling'] = self.allow_upscaling
        snap['preserve_aspect_ratio'] = self.preserve_aspect_ratio
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(ImageView, self).bind()
        attrs = (
            'source', 'scale_to_fit', 'allow_upscaling',
            'preserve_aspect_ratio',
        )
        self.publish_attributes(*attrs)

