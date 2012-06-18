#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Constant, Instance

from .list_view import ListView, AbstractTkListView


class AbstractTkThumbnailView(AbstractTkListView):
    """ The abstract toolkit interface for a ThumbnailView.

    Implementations should capitalize on the fact that the uniform
    item sizes flag is hard-coded to True and optimize their painting
    based on this.

    """
    pass


class ThumbnailView(ListView):
    """ A thin ListView subclass that allows for optimized thumbnail 
    rendering by hardcoding certain ListView options.

    """
    #: Hard code the uniform item sizes flag to True for a thumbnail
    #: viewer. This allows the widget to make certain assumptions 
    #: when drawing the thumbnails, which leads to drastically 
    #: improved performance.
    uniform_item_sizes = Constant(True)

    #: Initialize the view mode to 'icon', which will display the 
    #: text under the thumbnails. This is typically desired.
    view_mode = 'icon'

    #: Initialize some default item spacing, which gives the control
    #: a better appearance for thumbnails.
    item_spacing = 20

    #: Set the width hug to 'ignore' for the thumbnail view. The
    #: height hug is already set to 'ignore' on ListView.
    hug_width = 'ignore'

    #: Initialize the horizontal scrolling mode to smooth scroll by
    #: pixel which is the typical desired behavior.
    horizontal_scroll_mode = 'pixel'

    #: Initialize the vertical scrolling mode to smooth scroll by
    #: pixel which is the typical desired behavior.
    vertical_scroll_mode = 'pixel'

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkThumbnailView)

    def _icon_size_default(self):
        """ Provides a reasonable default icon size for thumbnails.

        """
        return (128, 128)

