from traits.api import Any, Callable, Int, Instance

from .control import IControlImpl, Control


class IImageImpl(IControlImpl):

    def parent_value_changed(self):
        raise NotImplementedError
    
    def parent_loader_changed(self):
        raise NotImplementedError
    
    def parent_width_changed(self):
        raise NotImplementedError
    
    def parent_height_changed(self):
        raise NotImplementedError


class Image(Control):
    """ A widget for displaying images.
    
    Attributes
    ----------
    value : Any
        A value that 'loader' knows how to convert into image data.     

    loader : Callable
        Converts 'value' into a 3D numpy array of RGB values:
        unsigned 8-bit integers with dimensions of height x width x 3.

    width : Int
        The width of the image in pixels. If the loader returns
        an array of different width, the image will be scaled to fit
        this width. This is not necessarily the size width of widget.

    height : Int
        The height of the image in pixels. If the loader returns
        an array of different size, the image will be scaled to fit
        this height. This is not necessarily the height of the widget.

    """
    value = Any

    loader = Callable
    
    width = Int
    
    height = Int

    #---------------------------------------------------------------------------
    # Overriddent parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IImageImpl)

    