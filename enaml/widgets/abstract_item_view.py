#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Event, Instance, List, Property, cached_property

from .base_component import BaseComponent
from .control import Control, AbstractTkControl

from ..item_models.abstract_item_model import AbstractItemModel
from ..item_models.model_index import ModelIndex
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

    #: The selection model for this view.
    selection_model = Property(depends_on='selection_children')
    
    #: The ModelIndex that has just been activated by a user interaction,
    #: usually a double-click or an Enter keypress.
    activated = Event(Instance(ModelIndex))

    #: The ModelIndex that has just been clicked.
    clicked = Event(Instance(ModelIndex))

    #: The ModelIndex that has just been double-clicked.
    double_clicked = Event(Instance(ModelIndex))

    #: Overridden parent class trait.
    abstract_obj = Instance(AbstractTkItemView)

    #: A filtered list of children containing the selection models
    selection_children = Property(List, depends_on='children')

    #: Overridden parent class trait to allow the item view to have
    #: at least one child.
    _subcomponents = List(Instance(BaseComponent), maxlen=1)

    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_selection_children(self):
        """ The property getter for the 'selection_children' attribute.

        """
        flt = lambda child: isinstance(child, BaseSelectionModel)
        return filter(flt, self.children)

    @cached_property
    def _get_selection_model(self):
        """ The property getter for the 'selection_model' attribute. It
        creates a default selection model if one is not provided as a 
        declarative subcomponent.

        """
        children = self.selection_children
        if len(children) == 0:
            res = BaseSelectionModel()
        else:
            res = children[0]
        return res
        

