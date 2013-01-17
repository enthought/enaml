#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod


class TabularModel(object):
    """ An abstract base class for supplying data to a tabular view.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def row_count(self):
        """ Get the number of rows in table.

        Returns
        -------
        result : int
            The number of rows in the table.

        """
        raise NotImplementedError

    @abstractmethod
    def column_count(self):
        """ Get the number of columns in the table.

        Returns
        -------
        result : int
            The number of columns in the table.

        """
        raise NotImplementedError

    @abstractmethod
    def data(self, rows, columns):
        """ Get the data for a span in the table.

        Parameters
        ----------
        rows : list
            The list of integer row indices for the span. The indices
            will be in model space, but may not be contiguous.

        columns : list
            The list of integer column indices for the span. The indices
            will be in model space, but may not be contiguous.

        Returns
        -------
        result : iterable or None
            A flat row-major iterable of data for the requested span.

        """
        raise NotImplementedError

    @abstractmethod
    def row_header_data(self, rows):
        """ Get the row header data for a span in the table.

        Parameters
        ----------
        rows : list
            The list of integer row indices for the span. The indices
            will be in model space, but may not be contiguous.

        Returns
        -------
        result : iterable or None
            An iterable of data for the requested span.

        """
        raise NotImplementedError

    @abstractmethod
    def column_header_data(self, columns):
        """ Get the column header data for a span in the table.

        Parameters
        ----------
        columns : list
            The list of integer column indices for the span. The indices
            will be in model space, but may not be contiguous.

        Returns
        -------
        result : iterable or None
            An iterable of data for the requested span.

        """
        raise NotImplementedError

    def row_styles(self, rows):
        """ Get the row styles for a span in the table.

        Parameters
        ----------
        rows : list
            The list of integer row indices for the span. The indices
            will be in model space, but may not be contiguous.

        Returns
        -------
        result : iterable or None
            An iterable of dictionary styles for the requested span.

        """
        return None

    def column_styles(self, columns):
        """ Get the column styles for a span in the table.

        Parameters
        ----------
        columns : list
            The list of integer column indices for the span. The indices
            will be in model space, but may not be contiguous.

        Returns
        -------
        result : iterable or None
            An iterable of dictionary styles for the requested span.

        """
        return None

    def cell_styles(self, rows, columns, data):
        """ Get the cell styles for a span in the table.

        Parameters
        ----------
        rows : list
            The list of integer row indices for the span. The indices
            will be in model space, but may not be contiguous.

        columns : list
            The list of integer column indices for the span. The indices
            will be in model space, but may not be contiguous.

        data : list
            The data values for the corresponding indices. This exists
            as a convenience so that the developer does not need to
            search for model data twice.

        Returns
        -------
        result : iterable or None
            A flat row-major iterable of dictionary styles for the
            requested span.

        """
        return None

    def row_header_styles(self, rows):
        """ Get the row header styles for a span in the table.

        Parameters
        ----------
        rows : list
            The list of integer row indices for the span. The indices
            will be in model space, but may not be contiguous.

        Returns
        -------
        result : iterable or None
            An iterable of dictionary styles for the requested span.

        """
        return None

    def column_header_styles(self, columns):
        """ Get the column header styles for a span in the table.

        Parameters
        ----------
        columns : list
            The list of integer column indices for the span. The indices
            will be in model space, but may not be contiguous.

        Returns
        -------
        result : iterable or None
            An iterable of dictionary styles for the requested span.

        """
        return None


class NullModel(TabularModel):

    def row_count(self):
        return 0

    def column_count(self):
        return 0

    def data(self, rows, columns):
        return None

    def row_header_data(self, rows):
        return None

    def column_header_data(self, columns):
        return None

