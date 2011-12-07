#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A ModelIndex class implemented in Cython for speed.

"""
cdef class ModelIndex:
    """ ModelIndexes are used to navigate an AbstractItemModel.

    A ModelIndex is a lightweight object and should be created on the
    fly, rather than attempting some form of caching. The user will
    not normally need to create indexes manually. Instead, use the
    create_index method on an AbstractItemModel.

    """
    cdef int _row, _column
    cdef object _model, _context 

    def __init__(self, int row, int column, context, model):
        """ Construct a model index.

        Arguments
        ---------
        row : int
            The row index represented by this index

        column : int
            The column index represented by this index

        model : AbstractItemModel
            The model in which this index is active. This is typically
            supplied by the create_index method of the AbstractItemModel.

        context : object
            A user supplied object that aids in navigating the user's
            model.

        """
        self._row = row
        self._column = column
        self._context = context
        self._model = model

    property row:
        
        def __get__(self):
            return self._row

    property column:
        
        def __get__(self):
            return self._column

    property context:

        def __get__(self):
            return self._context

    property model:

        def __get__(self):
            return self._model

    def __richcmp_(self, _other, int op):
        """ Performs a rich comparison operation on this index with another 
        index. The results of comparing this object with a non-ModelIndex 
        always returns False and therefore represents undefined behavior.

        """
        if not isinstance(_other, ModelIndex):
            return False
        
        cdef tuple this_tuple, other_tuple
        cdef ModelIndex other = _other

        this_tuple = (self._row, self._column, self._context, self._model)
        other_tuple = (other._row, other._column, other._context, other._model)

        # ==
        if op == 2:
            return this_tuple == other_tuple

        # !=
        if op == 3:
            return this_tuple != other_tuple

        # <
        if op == 0:
            return this_tuple < other_tuple
        
        # >
        if op == 4:
            return this_tuple > other_tuple
        
        # <=
        if op == 1:
            return this_tuple <= other_tuple
        
        # >=
        if op == 5:
            return this_tuple >= other_tuple
            
        return False
    
    def __repr__(self):
        msg = 'ModelIndex(row=%s, col=%s, context=%s, model=%s)'
        return msg % (self._row, self._column, self._context, self._model)
    
    def __str__(self):
        return self.__repr__()

    def parent(self):
        """ Returns the parent ModelIndex of this index.

        """
        return self._model.parent(self)
    
    def sibling(self, int row, int column):
        """ Returns the sibling ModelIndex of this index for the given
        row and column indexes.

        """
        cdef object model = self._model
        if self._row == row and self._column == column:
            return self
        return model.index(row, column, model.parent(self))
    
    def child(self, int row, int column):
        """ Returns the child ModelIndex of this index for the given
        row and column indexes.

        """
        return self._model.index(row, column, self)

    def flags(self):
        """ Returns the flags for this index.

        """
        return self._model.flags(self)

