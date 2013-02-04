#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from enaml.core.declarative import Declarative


class ItemModelProvider(Declarative):
    """ A base class for creating declarative item model providers.

    """
    def item_model(self):
        """ Get the item model associated with this provider.

        Returns
        -------
        result : AbstractItemModel
            A concrete implementation of AbstractItemModel.

        """
        raise NotImplementedError


class TableModelProvider(Declarative):
    """ A base class for creating declarative table model providers.

    """
    def table_model(self):
        """ Get the table model associated with this provider.

        Returns
        -------
        result : AbstractTableModel
            A concrete implementation of AbstractTableModel.

        """
        raise NotImplementedError

