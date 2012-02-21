#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Any, Callable, Int, Bool, Instance

from .control import Control, AbstractTkControl
from .abstract_pixmap import AbstractTkPixmap


class AbstractTkImage(AbstractTkControl):

    @abstractmethod
    def shell_pixmap_changed(self):
        raise NotImplementedError
    
    @abstractmethod
    def shell_img_width_changed(self):
        raise NotImplementedError

    @abstractmethod
    def shell_img_height_changed(self):
        raise NotImplementedError


class Image(Control):
    """ A widget for displaying images.

    """
    #: A Pixmap instance containing the image to display.
    pixmap = Instance(AbstractTkPixmap)
    
    #: Whether or not to scale the image with the size of the component
    scale_pixmap = Bool
    
    #: The width of the image in pixels. If the pixmap has a different width,
    #: the pixmap will be scaled to fit this width. This is not necessarily the
    #: width of widget.
    img_width = Int
    
    #: The height of the image in pixels. If the pixmap has a different height,
    #: the pixmap will be scaled to fit this height. This is not necessarily the
    #: height of widget.
    img_height = Int

    hug_width = 'weak'
    hug_height = 'weak'
    
    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkImage)

    