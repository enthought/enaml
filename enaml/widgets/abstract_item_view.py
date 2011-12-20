#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance, List, Property

from .control import Control, AbstractTkControl

from ..item_models.abstract_item_model import AbstractItemModel
from ..enums import SelectionMode, SelectionBehavior
from .base_item_selection_model import BaseItemSelectionModel


class AbstractTkItemView(AbstractTkControl):
    
    @abstractmethod
    def shell_item_model_changed(self, model):
        raise NotImplementedError

    @abstractmethod
    def set_selection_mode(self, selection_mode):
        raise NotImplementedError

    @abstractmethod
    def set_selection_behavior(self, selection_behavior):
        raise NotImplementedError


class AbstractItemView(Control):
    """ An abstract base class view that contains common logic for the
    ListView, TableView, and TreeView classes.
    
    """
    #: The AbstractItemModel instance being displayed by the view.
    item_model = Instance(AbstractItemModel)

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkItemView)

    #: The selection mode.
    selection_mode = SelectionMode()

    #: What kinds of things can be selected.
    selection_behavior = SelectionBehavior()

    #: The selection model for this view.
    selection_model = Property(Instance(BaseItemSelectionModel),
        depends_on=['_subcomponents', '_subcomponents_items'])

    _subcomponents = List(Instance(BaseItemSelectionModel), maxlen=1)

    def _selection_mode_changed(self, new):
        if self.abstract_obj is not None:
            self.abstract_obj.set_selection_mode(new)

    def _selection_behavior_changed(self, new):
        if self.abstract_obj is not None:
            self.abstract_obj.set_selection_behavior(new)

    def _subcomponents_default(self):
        return [BaseItemSelectionModel()]

    def _get_selection_model(self):
        return self._subcomponents[0]

