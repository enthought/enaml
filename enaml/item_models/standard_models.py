#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, Callable, Any, Int

from .abstract_item_model import (
    AbstractListModel, AbstractTableModel, ITEM_IS_SELECTABLE,
    ITEM_IS_ENABLED, ITEM_IS_EDITABLE
)


#------------------------------------------------------------------------------
# ModelMixin
#------------------------------------------------------------------------------
class ModelMixin(HasTraits):
    """ A mixin class that provides some basic functionality for
    standard models. This class should be inherited *before*
    any AbstractItemModel classes.

    """
    #: A user supplied object which will be querried using the 
    #: provided getters and setters.
    data_source = Any

    #: A user supplied callable that takes two arguments, the data
    #: source and an integer index, and returns a string for 
    #: display.
    data_getter = Callable

    #: A user supplied callable that takes three arguments, the
    #: data source, the integer index, and a string value and
    #: set the data on the model. If this callable is not 
    #: supplied, then this model will not be editable. The
    #: callable should return True on success, False otherwise.
    #: If True is returned, then an appropriate notification 
    #: message will be emitted to any attached views.
    data_setter = Callable

    #: An internal attribute used to store the value of the 
    #: flags when the data setter changes
    _flags = Int

    def __init__(self, data_source, **kwargs):
        """ Initialize a ListModel.

        Parameters
        ----------
        data_source : Any
            The data source object to use in this model
        
        **kwargs
            Any other attribute defaults.
        
        """
        # Set the data source quietly so we don't needlessly
        # trigger any traits listener updates
        self.trait_setq(data_source=data_source)
        super(ModelMixin, self).__init__(**kwargs)
    
    #--------------------------------------------------------------------------
    # Change and Default Value Handlers
    #--------------------------------------------------------------------------
    def _compute_flags(self):
        """ Computes the value for the internal flags attribute. If
        the user has not overridden the 'flags' method, this is the 
        value that will be used. By default, items are enabled and 
        selectable, and also editable if the user has supplied a
        data_setter callable.

        """
        flags = ITEM_IS_SELECTABLE | ITEM_IS_ENABLED
        if self.data_setter is not None:
            flags |= ITEM_IS_EDITABLE
        return flags

    def __flags_default(self):
        """ Returns the default value for the internal flags attribute.

        """
        return self._compute_flags()
    
    def _data_setter_changed(self):
        """ Recomputes the flags when the data setter has changed. 

        """
        # Since the only flag that is changing is whether or not an item 
        # is editable, we shouldn't need to send any messages to views as 
        # this should be querried on an as-needed basis.
        self._flags = self._compute_flags()

    def _data_source_changed(self):
        """ Notifies any attached views that our internal model has been
        reset and they should update their display.

        """
        self.begin_reset_model()
        self.end_reset_model()
    
    def _data_getter_changed(self):
        """ Notifies any attached views that our internal model has been
        reset and they should update their display.

        """
        self.begin_reset_model()
        self.end_reset_model()

    #--------------------------------------------------------------------------
    # AbstractItemModel Interface
    #--------------------------------------------------------------------------
    def flags(self, index):
        """ Returns the flags for the items in the model.

        """
        return self._flags


#------------------------------------------------------------------------------
# ListModel
#------------------------------------------------------------------------------
class ListModel(ModelMixin, AbstractListModel):
    """ An AbstractListModel implementation that provides some
    convenient defaults which make is easier to get up and running
    for a 1D data model. 

    The list model does not provide default facilities for customizing
    the appearance of items or anything to related header data. For that,
    the user should subclass ListModel and implement the appropriate
    methods of the AbstractListModel interface.

    """
    #: The default data getter callable
    data_getter = Callable(lambda src, idx: str(src[idx]))

    #--------------------------------------------------------------------------
    # AbstractItemModel interface
    #--------------------------------------------------------------------------
    def data(self, index):
        """ Returns the data point from the data source converted to a 
        string for display.

        """
        return self.data_getter(self.data_source, index.row)
    
    def set_data(self, index, value):
        """ Sets the data source with the converted value, emits the 
        proper changed notification and returns True. 

        """
        setter = self.data_setter
        if setter is not None:
            if setter(self.data_source, index.row, value):
                self.notify_data_changed(index, index)
                return True
        return False

    def row_count(self, parent=None):
        """ Returns the number of rows in the data source.

        """
        if parent is not None:
            return 0
        return len(self.data_source)


#------------------------------------------------------------------------------
# TableModel
#------------------------------------------------------------------------------
class TableModel(ModelMixin, AbstractTableModel):
    """ An AbstractTableModel implementation that provides some
    convenient defaults which make is easier to get up and running
    for a 2D data model. 

    The table model does not provide default facilities for customizing
    the appearance of items or anything related to header data. For that,
    the user should subclass TableModel and implement the appropriate
    methods of the AbstractTableModel interface.

    """
    #: The default data getter callable
    data_getter = Callable(lambda src, row, col: str(src[row][col]))

    #--------------------------------------------------------------------------
    # AbstractItemModel Interface
    #--------------------------------------------------------------------------
    def data(self, index):
        """ Returns the data point from the data source converted to a 
        string for display.

        """
        row = index.row
        col = index.column
        return self.data_getter(self.data_source, row, col)
    
    def set_data(self, index, value):
        """ Sets the data source with the converted value, emits the 
        proper changed notification and returns True. 

        """
        row = index.row
        col = index.column
        setter = self.data_setter
        if setter is not None:
            if setter(self.data_source, row, col, value):
                self.notify_data_changed(index, index)
                return True
        return False
        
    def row_count(self, parent=None):
        """ Returns the number of rows in the data source.

        """
        if parent is not None:
            return 0
        return len(self.data_source)
    
    def column_count(self, parent=None):
        """ Returns the number of columns in the data source.

        """
        if parent is not None:
            return 0
        return len(self.data_source[0])
        

#------------------------------------------------------------------------------
# ObjectModel (still work to do to sort this out)
#------------------------------------------------------------------------------
# class ObjectModel(TableModel):

#     #: The user supplied object that returns a string attribute
#     #: to get from an object when indexed with an integer.
#     fields = Any
    
#     def data(self, index):
#         """ Returns the data point from the data source converted to a 
#         string for display.

#         """
#         row = index.row
#         col = index.column
#         field = self.fields[col]
#         val = getattr(self.data_source[row], field)
#         return self._to_component(val)
    
#     def set_data(self, index, value):
#         """ Sets the data source with the converted value, emits the 
#         proper changed notification and returns True. 

#         """
#         row = index.row
#         col = index.column
#         field = self.fields[col]
#         val = self._from_component(value)
#         setattr(self.data_source[row], field, val)
#         self.notify_data_changed(index, index)
#         return True

#     def column_count(self, parent=None):
#         """ Returns the number of columns in the table.

#         """
#         if parent is not None:
#             return 0
#         return len(self.fields)

