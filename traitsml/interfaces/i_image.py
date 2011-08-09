from traits.api import Any, Callable, Int

from .i_element import IElement


class IImage(IElement):
    """A widget for displaying images."""
    
    # A value that `loader` knows how to convert into image data;
    # for example, a path name.
    value = Any

    # A Callable to convert `value` into a 3D numpy array of RGB values:
    # unsigned 8-bit integers with dimensions of width x height x 3.
    loader = Callable
    
    # The width of an image (in pixels).
    width = Int
    
    # The height of an image (in pixels).
    height = Int
