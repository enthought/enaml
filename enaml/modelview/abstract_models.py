#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from enaml.signaling import Signal


class AbstractItemModel(object):
    """ An abstract base class for creating item based models.

    """
    __metaclass__ = ABCMeta

    #: A signal which should be emitted when an item changes. The
    #: payload is the row and column index of the item that changed.
    item_changed = Signal()

    #: A signal which should be emitted when the entire model changes
    #: structure. Sometimes, this can be simpler and more efficient
    #: than the other notification signals. This signal has no payload.
    model_changed = Signal()

    #: A signal which should be emitted when rows are inserted. The
    #: payload should be the index of the insert and the number of
    #: rows inserted.
    rows_inserted = Signal()

    #: A signal which should be emitted when rows are removed. The
    #: payload should be the index of the removal and the number of
    #: rows removed.
    rows_removed = Signal()

    #: A signal which should be emitted when columns are inserted. The
    #: payload should be the index of the insert and the number of
    #: columns inserted.
    columns_inserted = Signal()

    #: A signal which should be emitted when columns are removed. The
    #: payload should be the index of the removal and the number of
    #: columns removed.
    columns_removed = Signal()

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


class NullItemModel(AbstractItemModel):
    """ A null implementation of AbstractItemModel.

    """
    def row_count(self):
        return 0

    def column_count(self):
        return 0

    def item_flags(self, row, column):
        return 0

    def item_data(self, row, column):
        return None


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


class NullTableModel(AbstractTableModel):
    """ A null implementation of AbstractTableModel.

    """
    def row_count(self):
        return 0

    def column_count(self):
        return 0

    def item_flags(self, row, column):
        return 0

    def item_data(self, row, column):
        return None

    def row_header_data(self, index):
        return None

    def column_header_data(self, index):
        return None

