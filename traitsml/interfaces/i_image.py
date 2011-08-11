from traits.api import Any, Callable, Int

from .i_element import IElement


class IImage(IElement):
    """ A widget for displaying images.
    
    Attributes
    ----------
    value : Any
        A value that `loader` knows how to convert into 
        image data.     

    loader : Callable
        Converts `value` into a 3D numpy array of RGB values:
        unsigned 8-bit integers with dimensions of width x height x 3.

    width : Int
        The width of the image in pixels. If the loader returns
        an array of different width, the image will be scaled to fit
        this width.

    height : Int
        The height of the image in pixels. If the loader returns
        an array of different size, the image will be scaled to fit
        this height.

    """
    value = Any

    loader = Callable
    
    width = Int
    
    height = Int


