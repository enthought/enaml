#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance

from .abstract_item_view import AbstractItemView, AbstractTkItemView


class AbstractTkListView(AbstractTkItemView):
    pass


class ListView(AbstractItemView):
    """ A view for list data.
    
    """
    #: How strongly a component hugs it's contents' height. ListViews 
    #: ignore the height hug by default, so they expand freely in height.
    hug_height = 'ignore'

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkListView)

