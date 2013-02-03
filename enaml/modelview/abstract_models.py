#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod


class AbstractItemModel(object):
    """ An abstract base class for creating item based models.

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
    def item_flags(self, row, column):
        """ Get the item flags for the given indices.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        Returns
        -------
        result : int
            An or'd combination of ItemFlag enum values for the given
            indices.

        """
        raise NotImplementedError

    @abstractmethod
    def item_data(self, row, column, role):
        """ Get the item data for the given indices and role.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        role : int
            One of the ItemDataRole enum values.

        Returns
        -------
        result : object or None
            The data value for the given indices and role, or None if
            no data is available.

        """
        raise NotImplementedError

    def set_item_data(self, row, column, value, role):
        """ Set the item data for the given indices and role.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        value : object
            The value entered by the user.

        role : int
            One of the ItemDataRole enum values.

        Returns
        -------
        result : bool
            True if the item was set successfully, False otherwise.

        """
        return False


class AbstractTableModel(AbstractItemModel):
    """ A abstract class for defining item based table models.

    A table model adds explicit support for row and column headers.

    """
    @abstractmethod
    def row_header_data(self, index, role):
        """ Get the row header data for the given index and role.

        Parameters
        ----------
        index : int
            The row index for the header.

        role : int
            One of the ItemDataRole enum values.

        Returns
        -------
        result : object or None
            The data value for the given index and role, or None if no
            data is available.

        """
        raise NotImplementedError

    @abstractmethod
    def column_header_data(self, index, role):
        """ Get the column header item for the given index.

        Parameters
        ----------
        index : int
            The column index for the header.

        role : int
            One of the ItemDataRole enum values.

        Returns
        -------
        result : object or None
            The data value for the given index and role, or None if no
            data is available.

        """
        raise NotImplementedError

