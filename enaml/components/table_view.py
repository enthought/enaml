#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance, Bool

from .abstract_item_view import AbstractItemView, AbstractTkItemView


class AbstractTkTableView(AbstractTkItemView):
    
    @abstractmethod
    def shell_vertical_header_visible_changed(self, visible):
        raise NotImplementedError
    
    @abstractmethod
    def shell_horizontal_header_visible_changed(self, visible):
        raise NotImplementedError


class TableView(AbstractItemView):
    """ A view for tabular data.
    
    """
    #: Whether or not the vertical header is shown. Defaults to True.
    vertical_header_visible = Bool(True)

    #: Whether or not the horizontal header is shown. Defaults to True.
    horizontal_header_visible = Bool(True)

    #: How strongly a component hugs it's contents' width. TableViews 
    #: ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'
    
    #: How strongly a component hugs it's contents' height. TableViews 
    #: ignore the height hug by default, so they expand freely in height.
    hug_height = 'ignore'

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkTableView)

