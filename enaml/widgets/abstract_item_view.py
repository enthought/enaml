#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance, Property, cached_property

from .base_selection_model import BaseSelectionModel
from .control import Control, AbstractTkControl

from ..core.trait_types import EnamlEvent
from ..item_models.abstract_item_model import AbstractItemModel
from ..item_models.model_index import ModelIndex


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

    #: The selection model for this view. If more than one selection
    #: model is declared and exception will be raised.
    selection_model = Property(
        Instance(BaseSelectionModel), depends_on='children',
    )
    
    #: The ModelIndex that has just been activated by a user interaction,
    #: usually a double-click or an Enter keypress.
    activated = EnamlEvent(ModelIndex)

    #: The ModelIndex that has just been clicked.
    clicked = EnamlEvent(ModelIndex)

    #: The ModelIndex that has just been double-clicked.
    double_clicked = EnamlEvent(ModelIndex)

    #: Overridden parent class trait.
    abstract_obj = Instance(AbstractTkItemView)

    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_selection_model(self):
        """ The property getter for the 'selection_model' attribute. It
        creates a default selection model if one is not provided.

        """
        flt = lambda child: isinstance(child, BaseSelectionModel)
        sel_models = filter(flt, self.children)
        n_models = len(sel_models)
        if n_models == 0:
            res = BaseSelectionModel()
        elif n_models == 1:
            res = sel_models[0]
        else:
            msg = 'An ItemView can have exactly 1 SelectionModel. %s given.'
            raise ValueError(msg % n_models)
        return res

