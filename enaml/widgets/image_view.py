#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Instance

from enaml.support.resource import ResourceHandle, ResourceID

from .control import Control


class ImageView(Control):
    """ A widget which can display an Image with optional scaling.

    """
    #: The image to display in the control
    image = Instance(ResourceHandle)

    image_id = ResourceID('image')

    #: Whether or not to scale the image with the size of the component.
    scale_to_fit = Bool(False)

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
    def snapshot(self):
        """ Returns the dict of creation attribute for the control.

        """
        snap = super(ImageView, self).snapshot()
        snap['scale_to_fit'] = self.scale_to_fit
        snap['preserve_aspect_ratio'] = self.preserve_aspect_ratio
        snap['allow_upscaling'] = self.allow_upscaling
        snap['image_id'] = self.image_id
        return snap

    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(ImageView, self).bind()
        self.publish_attributes(
            'scale_to_fit', 'preserve_aspect_ratio', 'allow_upscaling'
        )
        self.on_trait_change(self._send_image, 'image')

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def _send_image(self):
        """

        """
        content = {'image_id': self.image_id}
        self.send_action('set_image', content)

