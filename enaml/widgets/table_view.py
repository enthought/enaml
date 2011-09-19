#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance, Event

from .control import Control, IControlImpl

from ..item_models.abstract_item_model import AbstractItemModel, ModelIndex


class ITableViewImpl(IControlImpl):
    
    def parent_item_model_changed(self, item_model):
        raise NotImplementedError


class TableView(Control):

    item_model = Instance(AbstractItemModel)

    # The selected model index
    selected = Instance(ModelIndex)

    left_dclick = Event

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(ITableViewImpl)

TableView.protect('selected', 'left_dclick')

