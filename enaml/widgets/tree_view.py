#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance, Event

from .control import Control, AbstractTkControl

from ..item_models.abstract_item_model import AbstractItemModel


class AbstractTkTreeView(AbstractTkControl):
    
    @abstractmethod
    def shell_item_model_changed(self, item_model):
        raise NotImplementedError


class TreeView(Control):
    """ A view for tabular data.
    
    """
    #: The model for which this table is a view.
    item_model = Instance(AbstractItemModel)

    #: Fired after the left button is double-clicked.
    left_dclick = Event
    
    #: How strongly a component hugs it's contents' width.
    #: TableViews ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'
    
    #: How strongly a component hugs it's contents' height.
    #: TableViews ignore the height hug by default, so they expand freely in height.
    hug_height = 'ignore'

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkTreeView)

