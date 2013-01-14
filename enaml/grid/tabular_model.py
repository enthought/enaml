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
        result : iterable
            A flat row-major iterable of data for the requested span.

        """
        raise NotImplementedError

    @abstractmethod
    def horizontal_header_data(self, columns):
        """ Get the horizontal header data for a span in the table.

        Parameters
        ----------
        columns : list
            The list of integer column indices for the span. The indices
            will be in model space, but may not be contiguous.

        Returns
        -------
        result : iterable
            A flat row-major iterable of data for the requested span.

        """
        raise NotImplementedError

    @abstractmethod
    def vertical_header_data(self, rows):
        """ Get the vertical header data for a span in the table.

        Parameters
        ----------
        rows : list
            The list of integer row indices for the span. The indices
            will be in model space, but may not be contiguous.

        Returns
        -------
        result : iterable
            A flat row-major iterable of data for the requested span.

        """
        raise NotImplementedError


class NullModel(TabularModel):

    def row_count(self):
        return 0

    def column_count(self):
        return 0

    def data(self, rows, columns):
        return ()

    def horizontal_header_data(self, columns):
        return ()

    def vertical_header_data(self, rows):
        return ()

