#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str, Enum

from .resource import Resource


class Image(Resource):
    """ The basic Enaml image resource class.

    """
    #: The data of the image as a byte string
    data = Str

    #: The format of the image. By default, the consumer of the image
    #: will probe the header to automatically infer a type.
    format = Enum(
        'auto',     # Automatically determine the image format
        'png',      # Portable Network Graphics
        'jpg',      # Joint Photographic Experts Group
        'gif',      # Graphics Interchange Format
        'bmp',      # Windows Bitmap
        'xpm',      # X11 Pixmap
        'xbm',      # X11 Bitmap
        'pbm',      # Portable Bitmap
        'pgm',      # Portable Graymap
        'ppm',      # Portable Pixmap
        'tiff',     # Tagged Image File Format
    )

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get the snapshot dict for the Image.

        """
        snap = super(Image, self).snapshot()
        snap['data'] = self.data
        snap['format'] = self.format
        return snap

