#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance, List, Property

from .control import Control, AbstractTkControl

from ..item_models.abstract_item_model import AbstractItemModel
from .base_selection_model import BaseSelectionModel


class AbstractTkItemView(AbstractTkControl):
    
    @abstractmethod
    def shell_item_model_changed(self, model):
        raise NotImplementedError


class AbstractItemView(Control):
    """ An abstract base class view that contains common logic for the
    ListView, TableView, and TreeView classes.
    
    """
    #: The AbstractItemModel instance being displayed by the view.
    item_model = Instance(AbstractItemModel)

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkItemView)

    #: The selection model for this view.
    selection_model = Property(Instance(BaseSelectionModel),
        depends_on=['children'])

    _subcomponents = List(Instance(BaseSelectionModel), maxlen=1)

    def _subcomponents_default(self):
        return [BaseSelectionModel()]

    def _get_selection_model(self):
        return self._subcomponents[0]

