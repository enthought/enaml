#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Any, Callable, Int, Instance

from .control import Control, AbstractTkControl


class AbstractTkImage(AbstractTkControl):

    @abstractmethod
    def shell_value_changed(self):
        raise NotImplementedError
    
    @abstractmethod
    def shell_loader_changed(self):
        raise NotImplementedError
    
    @abstractmethod
    def shell_width_changed(self):
        raise NotImplementedError

    @abstractmethod
    def shell_height_changed(self):
        raise NotImplementedError


class Image(Control):
    """ A widget for displaying images.

    """
    #: A value that 'loader' knows how to convert into image data.
    value = Any

    #: Converts 'value' into a 3D numpy array of RGB values:
    #: unsigned 8-bit integers with dimensions of height x width x 3.
    loader = Callable
    
    #: The width of the image in pixels. If the loader returns
    #: an array of different width, the image will be scaled to fit
    #: this width. This is not necessarily the width of widget.
    img_width = Int
    
    #: The height of the image in pixels. If the loader returns
    #: an array of different size, the image will be scaled to fit
    #: this height. This is not necessarily the height of the widget.
    img_height = Int

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkImage)

    