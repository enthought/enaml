#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from .component import Component, AbstractTkComponent

from ..enums import SelectionMode, SelectionBehavior
from ..core.trait_types import EnamlEvent


class AbstractTkBaseSelectionModel(AbstractTkComponent):
    """ The toolkit interface for the selection model.

    """
    @abstractmethod
    def clear(self):
        """ Clear the selection and the current index.

        """
        raise NotImplementedError

    @abstractmethod
    def get_current_index(self):
        """ Return the current ModelIndex or None if there is not one.

        """
        raise NotImplementedError

    @abstractmethod
    def set_current_index(self, index):
        """ Set the current ModelIndex.

        """
        raise NotImplementedError

    @abstractmethod
    def set_selection(self, selection, command='clear_select'):
        """ Set the current selection.

        """
        raise NotImplementedError

    @abstractmethod
    def get_selection(self):
        """ Get the current selection.

        """
        raise NotImplementedError

    @abstractmethod
    def set_selection_mode(self, selection_mode):
        raise NotImplementedError

    @abstractmethod
    def set_selection_behavior(self, selection_behavior):
        raise NotImplementedError


class BaseSelectionModel(Component):
    """ The base class for item selection models.

    """
    #: Updated when the current ModelIndex changes. Gets a 2-tuple of
    #: (old ModelIndex, new ModelIndex)
    current_event = EnamlEvent

    #: Updated when the current selection changes. Gets a 2-tuple of
    #: (deleted items, added items). Each selection is a list of
    #: (top_left ModelIndex, bottom_right ModelIndex) tuples specifying
    #: rectangular ranges of selected cells.
    selection_event = EnamlEvent

    #: The selection mode.
    selection_mode = SelectionMode

    #: What kinds of things can be selected.
    selection_behavior = SelectionBehavior

    def clear(self):
        """ Clear the selection and the current index.

        """
        self.abstract_obj.clear()

    def set_current_index(self, index):
        """ Set the current ModelIndex.

        This is the cell used for keyboard focus and is usually set when
        the user clicks a cell. This may be independent of the selection. 
        It is frequently rendered with a dashed border.

        Parameters
        ----------
        index : ModelIndex
            The index to make current.

        """
        self.abstract_obj.set_current_index(index)

    def get_current_index(self):
        """ Get the current ModelIndex.

        """
        return self.abstract_obj.get_current_index()

    def set_selection(self, selection, command='clear_select'):
        """ Set the current selection.

        Parameters
        ----------
        selection : list of (ModelIndex, ModelIndex) tuples
            Each tuple is an inclusive range specifying a bounding box
            for a given selection range.
            
        command : single or sequence of SelectionCommand, optional
            Exactly what action to perform given these selection ranges. 
            See the `SelectionCommand` documentation for the complete 
            set. Sequences of SelectionCommands will be treated as 
            binary-ORing the flags.
        
        """
        self.abstract_obj.set_selection(selection, command)

    def get_selection(self):
        """ Get the current selection.

        Returns
        -------
        selection : list of (ModelIndex, ModelIndex) tuples
            Each tuple is an inclusive range specifying a bounding box 
            for a given selection range.

        """
        return self.abstract_obj.get_selection()

    def _selection_mode_changed(self, new):
        if self.abstract_obj is not None:
            self.abstract_obj.set_selection_mode(new)

    def _selection_behavior_changed(self, new):
        if self.abstract_obj is not None:
            self.abstract_obj.set_selection_behavior(new)

