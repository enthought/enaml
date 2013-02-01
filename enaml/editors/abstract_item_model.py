#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod


class AbstractItemModel(object):
    """ An abstract base class for creating item-based view models.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def row_count(self):
        """ Get the number of rows in the model.

        Returns
        -------
        result : int
            The number of rows in the model.

        """
        raise NotImplementedError

    @abstractmethod
    def column_count(self):
        """ Get the number of columns in the model.

        Returns
        -------
        result : int
            The number of columns in the model.

        """
        raise NotImplementedError

    @abstractmethod
    def item(self, row, column):
        """ Get the item for the given indices.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        Returns
        -------
        result : Item or None
            The item instance for the given indices, or None if there
            is no item available.

        """
        raise NotImplementedError

