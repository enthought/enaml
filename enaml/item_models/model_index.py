#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
class ModelIndex(tuple):
    """ ModelIndexes are used to navigate an AbstractItemModel.

    A ModelIndex is a lightweight object and should be created on the
    fly, rather than attempting some form of caching. The user will
    not normally need to create indexes manually. Instead, use the
    create_index method on an AbstractItemModel.

    """
    __slots__ = ()
    
    def __new__(cls, row, column, context, model):
        """ Construct a model index.

        Arguments
        ---------
        row : int
            The row index represented by this index.

        column : int
            The column index represented by this index

        context : object
            A user supplied object that aids in navigating the user's
            model.

        model : AbstractItemModel
            The model in which this index is active. This is typically
            supplied by the create_index method of the AbstractItemModel.

        """
        return tuple.__new__(cls, (row, column, context, model))

    def __repr__(self):
        return 'ModelIndex(row=%s, col=%s, context=%s, model=%s)' % self
    
    def __str__(self):
        return self.__repr__()

    @property
    def row(self):
        return self[0]
    
    @property
    def column(self):
        return self[1]
    
    @property
    def context(self):
        return self[2]

    @property
    def model(self):
        return self[3]
        
    def parent(self):
        """ Returns the parent ModelIndex of this index.

        """
        return self.model.parent(self)

    def sibling(self, row, column):
        """ Returns the sibling ModelIndex of this index for the given
        row and column indexes.

        """
        model = self.model
        if self.row == row and self.column == column:
            return self
        return model.index(row, column, model.parent(self))

    def child(self, row, column):
        """ Returns the child ModelIndex of this index for the given
        row and column indexes.

        """
        return self.model.index(row, column, self)

    def flags(self):
        """ Returns the flags for this index.

        """
        return self.model.flags(self)


# Use the faster Cython implemented ModelIndex if available
try:
    from ..speedups.model_index import ModelIndex
except ImportError:
    pass

