#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Event, List

from .base_component import BaseComponent, AbstractTkBaseComponent


class AbstractTkBaseItemSelectionModel(AbstractTkBaseComponent):
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


class BaseItemSelectionModel(BaseComponent):
    """ The base class for item selection models.

    """

    #: Updated when the current ModelIndex changes.
    #: Gets a 2-tuple: (old ModelIndex, new ModelIndex)
    current_event = Event()

    #: Updated when the current selection changes.
    #: Gets a 2-tuple: (old selection, new selection)
    #: Each selection is a list of
    #: (top_left ModelIndex, bottom_right ModelIndex) tuples specifying
    #: rectangular ranges of selected cells.
    selection_event = Event()

    #: BaseItemSelectionModels are not visible.
    visible = False

    #: BaseItemSelectionModel has no children.
    _subcomponents = List(maxlen=0)


    def clear(self):
        """ Clear the selection and the current index.

        """
        self.abstract_obj.clear()

    def set_current_index(self, index):
        """ Set the current ModelIndex.

        This is the cell used for keyboard focus and is usually set when the
        user clicks on a cell. This may be independent of the selection. It is
        frequently rendered with a dashed border.

        Parameters
        ----------
        index : ModelIndex
            The index to make current.

        """
        self.abstract_obj.set_current_index(index)

    def get_current_index(self):
        """ Get the current ModelIndex.

        """
        return self.abstract_obj.get_current_index(index)

    def set_selection(self, selection, command='clear_select'):
        """ Set the current selection.

        Parameters
        ----------
        selection : list of (ModelIndex, ModelIndex) tuples
            Each tuple is an inclusive range specifying a bounding box for
            a given selection range.
        command : SelectionCommand or sequence of SelectionCommands, optional
            Exactly what action to perform given these selection ranges. See the
            `SelectionCommand` documentation for the complete set. Sequences of
            SelectionCommands will be treated as binary-ORing the flags.
        """
        self.abstract_obj.set_selection(selection, command)

    def get_selection(self):
        """ Get the current selection.

        Returns
        -------
        selection : list of (ModelIndex, ModelIndex) tuples
            Each tuple is an inclusive range specifying a bounding box for
            a given selection range.
        """
        return self.abstract_obj.get_selection()

