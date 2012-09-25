#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Str, Instance, Property, cached_property

from enaml.noncomponents.image.abstract_image import AbstractImage

from .constraints_widget import ConstraintsWidget


class ImageView(ConstraintsWidget):
    """ A widget which can display an Image with optional scaling.

    """
    #: The image to display in the control
    image = Instance(AbstractImage)
    
    #: The image to display in the control
    image_id = Property(Str, depends_on='image')
    
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
            'scale_to_fit', 'preserve_aspect_ratio', 'allow_upscaling',
            'image_id'
        )

    def on_action_snap_image(self, content):
        """ A change handler invoked when the image changes.
        
        """
        snap = self.image.snapshot()
        self.send_action('snap_image_response', snap)
            

    #--------------------------------------------------------------------------
    # Traits Handlers
    #--------------------------------------------------------------------------
    @cached_property
    def _get_image_id(self):
        """ Extract the object_id from the Image
        
        """
        if self.image is not None:
            return self.image.object_id
