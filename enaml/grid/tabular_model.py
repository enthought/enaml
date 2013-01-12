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

        """
        raise NotImplementedError


class NullModel(TabularModel):

    def row_count(self):
        return 0

    def column_count(self):
        return 0

    def data(self, rows, columns):
        return ()

