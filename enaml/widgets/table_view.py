from traits.api import Instance

from .control import Control, IControlImpl

from ..item_models.abstract_item_model import AbstractItemModel


class ITableViewImpl(IControlImpl):
    
    def parent_item_model_changed(self, item_model):
        raise NotImplementedError


class TableView(Control):

    item_model = Instance(AbstractItemModel)

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(ITableViewImpl)

