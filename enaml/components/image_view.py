#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Bool, Instance

from .control import Control, AbstractTkControl

from ..noncomponents.abstract_image import AbstractTkImage


class AbstractTkImageView(AbstractTkControl):
    """ The abstract toolkit interface for an ImageView.

    """
    @abstractmethod
    def shell_image_changed(self):
        """ The change handler for the 'image' attribute on the shell 
        component.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_scale_to_fit_changed(self):
        """ The change handler for the 'scale_to_fit' attribute on the 
        shell component.

        """
        raise NotImplementedError


class ImageView(Control):
    """ A simple viewer for instances of AbstractTkImage.

    """
    #: A Pixmap instance containing the image to display.
    image = Instance(AbstractTkImage)
    
    #: Whether or not to scale the image with the size of the component.
    scale_to_fit = Bool(False)
    
    #: An image view hugs its width weakly by default.
    hug_width = 'weak'

    #: An image view hugs its height weakly by default.
    hug_height = 'weak'
    
    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkImageView)

