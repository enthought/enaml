#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance

from .control import Control, AbstractTkControl

from ..item_models.abstract_item_model import AbstractItemModel


class AbstractTkItemView(AbstractTkControl):
    
    @abstractmethod
    def shell_item_model_changed(self, model):
        raise NotImplementedError

    @abstractmethod
    def shell_selection_model_changed(self, model):
        raise NotImplementedError


class AbstractItemView(Control):
    """ An abstract base class view that contains common logic for the
    ListView, TableView, and TreeView classes.
    
    """
    #: The AbstractItemModel instance being displayed by the view.
    item_model = Instance(AbstractItemModel)

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkItemView)

