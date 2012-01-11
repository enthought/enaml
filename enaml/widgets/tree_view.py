#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance, Bool

from .abstract_item_view import AbstractItemView, AbstractTkItemView


class AbstractTkTreeView(AbstractTkItemView):
    
    @abstractmethod
    def shell_header_visible_changed(self, visible):
        raise NotImplementedError


class TreeView(AbstractItemView):
    """ A view for tree data.
    
    """
    #: Whether or not the tree header is visible. Defaults to True.
    header_visible = Bool(True)

    #: How strongly a component hugs it's contents' height. TreeViews 
    #: ignore the height hug by default, so they expand freely in height.
    hug_height = 'ignore'

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkTreeView)

