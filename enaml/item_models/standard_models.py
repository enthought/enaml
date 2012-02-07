#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .abstract_item_model import (
    AbstractListModel, AbstractTableModel, ITEM_IS_SELECTABLE,
    ITEM_IS_ENABLED, ITEM_IS_EDITABLE,
)


#------------------------------------------------------------------------------
# List Model
#------------------------------------------------------------------------------
class ListModel(AbstractListModel):
    """ A concrete implementation of AbstractListModel which is intended
    to be easy to use for data models which behave more-or-less like
    one dimensional sequences.

    The data object can be updated dynamically after instantiation by 
    using the 'data_source' property.

    """
    base_flags = ITEM_IS_ENABLED | ITEM_IS_SELECTABLE

    def __init__(self, data, editable=False, display_data_converter=unicode,
                 edit_data_converter=None, background_brush_func=None, 
                 foreground_brush_func=None, font_func=None, 
                 vertical_headers=None, horizontal_headers=None):
        """ Initialize a ListModel.

        Parameters
        ----------
        data : 1D sequence-like object
            A sequence-like object that provides the data for the model.
            At a minimum it must support __getitem__ and __len__, and
            if editable, __setitem__.
        
        editable : bool, optional
            A bool which indicates whether or not the model is editable.
            If True, editing a cell will be done with an editor that is
            appropriate for the type of data given in the model. The
            default is False.
            
        display_data_converter : callable, optional
            An optional callable which should take a single argument: the
            value for the cell, and return a unicode value to use as the
            display value in the cell. The default value is the builtin
            unicode object.
        
        edit_data_converter : callable or None, optional
            An optional callable which should take a single argument: the
            unicode value typed by the user, and return a value to set
            in the model. This converter is only used when the model is
            declared as editable. If this converter is not supplied and
            the model is editable, then the type of the converted value
            will be determined automatically based on the input type. If
            a converter is supplied, and it cannot convert the value, it
            should raise a ValueError and the change will be ignored. The
            default value is None.
        
        background_brush_func : callable or None, optional
            If provided, it should be a callable which accepts two 
            arguments: the data value and the row index, and returns
            a brush for the background of the cell. The default is
            None.
        
        foreground_brush_func : callable or None, optional
            If provided, it should be a callable which accepts two 
            arguments: the data value and the row index, and returns
            a brush for the foreground of the cell. The default is
            None.
        
        font_func : callable or None, optional
            If provided, it should be a callable which accepts two 
            arguments: the data value and the row index, and returns
            a font for the cell. The default is None.
        
        vertical_headers : sequence-like object or None
            If provided, is should be a sequence like object which
            will be indexed with an integer index to retrieve a
            unicode string for the given row header. 
        
        horizontal_headers : sequence-like object or None
            If provided, is should be a sequence like object which
            will be indexed with an integer index to retrieve a
            unicode string for the given column header.

        """
        self._data_source = data
        self._editable = editable
        self._display_data_converter = display_data_converter
        self._edit_data_converter = edit_data_converter
        self._background_brush_func = background_brush_func
        self._foreground_brush_func = foreground_brush_func
        self._font_func = font_func
        self._vertical_headers = vertical_headers
        self._horizontal_headers = horizontal_headers

    def _get_data_source(self):
        """ The property getter for the 'data_source' property.
        
        """
        return self._data_source
    
    def _set_data_source(self, data):
        """ The property setter for the 'data_source' property.    
        
        """
        self.begin_reset_model()
        self._data_source = data
        self.end_reset_model()
    
    data_source = property(_get_data_source, _set_data_source)

    def flags(self, index):
        """ Returns the flags for the items in the model.

        """
        flags = self.base_flags
        if self._editable:
            flags |= ITEM_IS_EDITABLE
        return flags

    def data(self, index):
        """ Returns the data point from the data source converted to a 
        unicode for display.

        """
        return self._display_data_converter(self._data_source[index.row])
    
    def edit_data(self, index):
        """ Returns the data value for editing. If an edit converter is
        provided, then the unicode form of the data is returned, 
        otherwise, the raw datapoint is returned.

        """
        if self._edit_data_converter is None:
            return self._data_source[index.row]
        return self.data(index)
    
    def set_data(self, index, value):
        """ Sets the data source with the converted value, emits the 
        proper changed notification and returns True. 

        """
        converter = self._edit_data_converter
        if converter is not None:
            try:
                value = converter(value)
            except ValueError:
                return False
        self._data_source[index.row] = value
        self.notify_data_changed(index, index)
        return True

    def row_count(self, parent=None):
        """ Returns the number of rows in the data source.

        """
        if parent is not None:
            return 0
        return len(self._data_source)

    def background(self, index):
        """ Returns the brush for the background of the given index,
        or None.

        """
        brush_func = self._background_brush_func
        if brush_func is not None:
            row = index.row
            return brush_func(self._data_source[row], row)
    
    def foreground(self, index):
        """ Returns the brush for the foreground of the given index,
        or None.

        """
        brush_func = self._foreground_brush_func
        if brush_func is not None:
            row = index.row
            return brush_func(self._data_source[row], row)

    def font(self, index):
        """ Returns the font for the foreground of the given index,
        or None.

        """
        font_func = self._font_func
        if font_func is not None:
            row = index.row
            return font_func(self._data_source[row], row)

    def vertical_header_data(self, section):
        """ Returns the vertical header data for the given section.

        """
        headers = self._vertical_headers
        if headers is not None:
            res = headers[section]
        else:
            sup = super(ListModel, self)
            res = sup.vertical_header_data(section)
        return res
    
    def horizontal_header_data(self, section):
        """ Returns the horiztonal header data for the given section.

        """
        headers = self._horizontal_headers
        if headers is not None:
            res = headers[section]
        else:
            sup = super(ListModel, self)
            res = sup.horizontal_header_data(section)
        return res


#------------------------------------------------------------------------------
# Table Model
#------------------------------------------------------------------------------
class TableModel(AbstractTableModel):
    """ A concrete implementation of AbstractTableModel which is intended
    to be easy to use for data models which behave like two dimensional
    arrays.

    The data object can be updated dynamically after instantiation by 
    using the 'data_source' property.

    """
    base_flags = ITEM_IS_ENABLED | ITEM_IS_SELECTABLE

    def __init__(self, data, editable=False, display_data_converter=unicode,
                 edit_data_converter=None, background_brush_func=None, 
                 foreground_brush_func=None, font_func=None,
                 vertical_headers=None, horizontal_headers=None):
        """ Initialize a TableModel.

        Parameters
        ----------
        data : 2D array-like object
            An array-like object that provides the data for the model.
            At a minimum it must support __getitem__ which can be
            indexed with a (row, col) tuple, and have a 'shape' attribute
            which gives an (nrows, ncols) tuple. If the model is also
            editable, it should support __setitem__

        editable : bool, optional
            A bool which indicates whether or not the model is editable.
            If True, editing a cell will be done with an editor that is
            appropriate for the type of data given in the model. The
            default is False.
            
        display_converter : callable, optional
            An optional callable which should take a single argument: the
            value for the cell, and return a unicode value to use as the
            display value in the cell. The default value is the builtin
            unicode object.
        
        edit_converter : callable or None, optional
            An optional callable which should take a single argument: the
            unicode value typed by the user, and return a value to set
            in the model. This converter is only used when the model is
            declared as editable. If this converter is not supplied and
            the model is editable, then the type of the converted value
            will be determined automatically based on the input type. If
            a converter is supplied, and it cannot convert the value, it
            should raise a ValueError and the change will be ignored. The
            default value is None.
        
        background_brush_func : callable or None, optional
            If provided, it should be a callable which accepts three
            arguments: the data value, the row index and column index, 
            and returns a brush for the background of the cell. The 
            default is None.
        
        foreground_brush_func : callable or None, optional
            If provided, it should be a callable which accepts three
            arguments: the data value, the row index and column index, 
            and returns a brush for the foreground of the cell. The 
            default is None.
        
        font_func : callable or None, optional
            If provided, it should be a callable which accepts three
            arguments: the data value, the row index and column index, 
            and returns a font for the cell. The default is None.

        vertical_headers : sequence-like object or None
            If provided, is should be a sequence like object which
            will be indexed with an integer index to retrieve a
            unicode string for the given row header. 
        
        horizontal_headers : sequence-like object or None
            If provided, is should be a sequence like object which
            will be indexed with an integer index to retrieve a
            unicode string for the given column header.

        """
        self._data_source = data
        self._editable = editable
        self._display_data_converter = display_data_converter
        self._edit_data_converter = edit_data_converter
        self._background_brush_func = background_brush_func
        self._foreground_brush_func = foreground_brush_func
        self._font_func = font_func
        self._vertical_headers = vertical_headers
        self._horizontal_headers = horizontal_headers
    
    def _get_data_source(self):
        """ The property getter for the 'data_source' property.
        
        """
        return self._data_source
    
    def _set_data_source(self, data):
        """ The property setter for the 'data_source' property.    
        
        """
        self.begin_reset_model()
        self._data_source = data
        self.end_reset_model()
    
    data_source = property(_get_data_source, _set_data_source)

    def flags(self, index):
        """ Returns the flags for the items in the model.

        """
        flags = self.base_flags
        if self._editable:
            flags |= ITEM_IS_EDITABLE
        return flags

    def data(self, index): 
        """ Returns the data point from the data source converted to a 
        unicode for display.

        """
        row = index.row
        col = index.column
        return self._display_data_converter(self._data_source[row, col])
    
    def edit_data(self, index):
        """ Returns the data value for editing. If an edit converter is
        provided, then the unicode form of the data is returned, 
        otherwise, the raw datapoint is returned.

        """
        if self._edit_data_converter is None:
            row = index.row
            col = index.column
            return self._data_source[row, col]
        return self.data(index)
    
    def set_data(self, index, value):
        """ Sets the data source with the converted value, emits the 
        proper changed notification and returns True. 

        """
        converter = self._edit_data_converter
        if converter is not None:
            try:
                value = converter(value)
            except ValueError:
                return False
        row = index.row
        col = index.column
        self._data_source[row, col] = value
        self.notify_data_changed(index, index)
        return True
        
    def row_count(self, parent=None):
        """ Returns the number of rows in the data source.

        """
        if parent is not None:
            return 0
        return self._data_source.shape[0]
    
    def column_count(self, parent=None):
        """ Returns the number of columns in the data source.

        """
        if parent is not None:
            return 0
        return self._data_source.shape[1]

    def background(self, index):
        """ Returns the brush for the background of the given index,
        or None.

        """
        brush_func = self._background_brush_func
        if brush_func is not None:
            row = index.row
            col = index.column
            return brush_func(self._data_source[row, col], row, col)
    
    def foreground(self, index):
        """ Returns the brush for the foreground of the given index,
        or None.

        """
        brush_func = self._foreground_brush_func
        if brush_func is not None:
            row = index.row
            col = index.column
            return brush_func(self._data_source[row, col], row, col)

    def font(self, index):
        """ Returns the font for the foreground of the given index,
        or None.

        """
        font_func = self._font_func
        if font_func is not None:
            row = index.row
            col = index.column
            return font_func(self._data_source[row, col], row, col)

    def vertical_header_data(self, section):
        """ Returns the vertical header data for the given section.

        """
        headers = self._vertical_headers
        if headers is not None:
            res = headers[section]
        else:
            sup = super(TableModel, self)
            res = sup.vertical_header_data(section)
        return res
    
    def horizontal_header_data(self, section):
        """ Returns the horiztonal header data for the given section.

        """
        headers = self._horizontal_headers
        if headers is not None:
            res = headers[section]
        else:
            sup = super(TableModel, self)
            res = sup.horizontal_header_data(section)
        return res


#------------------------------------------------------------------------------
# Object Model
#------------------------------------------------------------------------------
class ObjectModel(AbstractTableModel):
    """ A concrete implementation of AbstractTableModel which is intended
    to be easy to use for data models which display list of objects 
    where each object corresponds to a row in the table.

    The data object can be updated dynamically after instantiation by 
    using the 'data_source' property.

    """
    base_flags = ITEM_IS_ENABLED | ITEM_IS_SELECTABLE

    @staticmethod
    def format_header(header):
        """ A simple formatter class which converts an attribute name
        in a form more-or-less suitable for a column header.

        """
        return ' '.join(s.capitalize() for s in header.split('_'))

    def __init__(self, data, transpose=False, editable=False, 
                 display_data_converter=unicode, edit_data_converter=None, 
                 background_brush_func=None, foreground_brush_func=None, 
                 font_func=None, vertical_headers=None, 
                 horizontal_headers=None):
        """ Initialize an ObjectModel.

        Parameters
        ----------
        data : a 2-tuple of (object, column_attributes)
            A tuple whose first element is a sequence-like object that
            provides the row objects for the model, and whose second
            element is a sequence-like object that provides the string 
            names of the attributes of the objects which provide the
            data for the columns. At a minimum both elements must support
            __getitem__ and __len__.

        transpose : bool, optional
            A boolean which indicates that the model should be transposed
            such that the objects represent columns and the attributes
            represent rows. The default is False.

        editable : bool, optional
            A bool which indicates whether or not the model is editable.
            If True, editing a cell will be done with an editor that is
            appropriate for the type of data given in the model. The
            default is False.
            
        display_converter : callable, optional
            An optional callable which should take a single argument: the
            value for the cell, and return a unicode value to use as the
            display value in the cell. The default value is the builtin
            unicode object.
        
        edit_converter : callable or None, optional
            An optional callable which should take a single argument: the
            unicode value typed by the user, and return a value to set
            in the model. This converter is only used when the model is
            declared as editable. If this converter is not supplied and
            the model is editable, then the type of the converted value
            will be determined automatically based on the input type. If
            a converter is supplied, and it cannot convert the value, it
            should raise a ValueError and the change will be ignored. The
            default value is None.
        
        background_brush_func : callable or None, optional
            If provided, it should be a callable which accepts three
            arguments: the data value, the row index and column index, 
            and returns a brush for the background of the cell. The 
            default is None.
        
        foreground_brush_func : callable or None, optional
            If provided, it should be a callable which accepts three
            arguments: the data value, the row index and column index, 
            and returns a brush for the foreground of the cell. The 
            default is None.
        
        font_func : callable or None, optional
            If provided, it should be a callable which accepts three
            arguments: the data value, the row index and column index, 
            and returns a font for the cell. The default is None.

        vertical_headers : sequence-like object or None
            If provided, is should be a sequence like object which
            will be indexed with an integer index to retrieve a
            unicode string for the given row header. 
        
        horizontal_headers : sequence-like object or None
            If provided, is should be a sequence like object which
            will be indexed with an integer index to retrieve a
            unicode string for the given column header.

        """
        self._data_source = data
        self._transpose = transpose
        self._editable = editable
        self._display_data_converter = display_data_converter
        self._edit_data_converter = edit_data_converter
        self._background_brush_func = background_brush_func
        self._foreground_brush_func = foreground_brush_func
        self._font_func = font_func
        self._vertical_headers = vertical_headers
        self._horizontal_headers = horizontal_headers
    
    def _get_data_source(self):
        """ The property getter for the 'data_source' property.
        
        """
        return self._data_source
    
    def _set_data_source(self, data):
        """ The property setter for the 'data_source' property.    
        
        """
        self.begin_reset_model()
        self._data_source = data
        self.end_reset_model()
    
    data_source = property(_get_data_source, _set_data_source)

    def _get_transpose(self):
        """ The property getter for the 'transpose' property.

        """
        return self._transpose
    
    def _set_transpose(self, value):
        """ The property setter for the 'transposed' property.

        """
        self.begin_reset_model()
        self._transpose = value
        self.end_reset_model()
    
    transpose = property(_get_transpose, _set_transpose)
    
    def flags(self, index):
        """ Returns the flags for the items in the model.

        """
        flags = self.base_flags
        if self._editable:
            flags |= ITEM_IS_EDITABLE
        return flags

    def data(self, index): 
        """ Returns the data point from the data source converted to a 
        unicode for display.

        """
        row = index.row
        col = index.column
        if self._transpose:
            row, col = col, row
        objs, attrs = self._data_source
        value = getattr(objs[row], attrs[col])
        return self._display_data_converter(value)
    
    def edit_data(self, index):
        """ Returns the data value for editing. If an edit converter is
        provided, then the unicode form of the data is returned, 
        otherwise, the raw datapoint is returned.

        """
        if self._edit_data_converter is None:
            row = index.row
            col = index.column
            if self._transpose:
                row, col = col, row
            objs, attrs = self._data_source
            return getattr(objs[row], attrs[col])
        return self.data(index)
    
    def set_data(self, index, value):
        """ Sets the data source with the converted value, emits the 
        proper changed notification and returns True. 

        """
        converter = self._edit_data_converter
        if converter is not None:
            try:
                value = converter(value)
            except ValueError:
                return False
        row = index.row
        col = index.column
        if self._transpose:
            row, col = col, row
        objs, attrs = self._data_source
        setattr(objs[row], attrs[col], value)
        self.notify_data_changed(index, index)
        return True
        
    def row_count(self, parent=None):
        """ Returns the number of rows in the data source.

        """
        if parent is not None:
            return 0
        idx = 0
        if self._transpose:
            idx = 1
        return len(self._data_source[idx])
    
    def column_count(self, parent=None):
        """ Returns the number of columns in the data source.

        """
        if parent is not None:
            return 0
        idx = 1
        if self._transpose:
            idx = 0
        return len(self._data_source[idx])

    def background(self, index):
        """ Returns the brush for the background of the given index,
        or None.

        """
        brush_func = self._background_brush_func
        if brush_func is not None:
            row = index.row
            col = index.column
            if self._transpose:
                row, col = col, row
            objs, attrs = self._data_source
            value = getattr(objs[row], attrs[col])
            return brush_func(value, row, col)
    
    def foreground(self, index):
        """ Returns the brush for the foreground of the given index,
        or None.

        """
        brush_func = self._foreground_brush_func
        if brush_func is not None:
            row = index.row
            col = index.column
            if self._transpose:
                row, col = col, row
            objs, attrs = self._data_source
            value = getattr(objs[row], attrs[col])
            return brush_func(value, row, col)

    def font(self, index):
        """ Returns the font for the foreground of the given index,
        or None.

        """
        font_func = self._font_func
        if font_func is not None:
            row = index.row
            col = index.column
            if self._transpose:
                row, col = col, row
            objs, attrs = self._data_source
            value = getattr(objs[row], attrs[col])
            return font_func(value, row, col)

    def vertical_header_data(self, section):
        """ Returns the vertical header data for the given section.

        """
        headers = self._vertical_headers
        if headers is not None:
            res = headers[section]
        else:
            if self._transpose:
                res = self.format_header(self._data_source[1][section])
            else:
                sup = super(ObjectModel, self)
                res = sup.vertical_header_data(section)
        return res
    
    def horizontal_header_data(self, section):
        """ Returns the horiztonal header data for the given section.

        """
        headers = self._horizontal_headers
        if headers is not None:
            res = headers[section]
        else:
            if not self._transpose:
                res = self.format_header(self._data_source[1][section])
            else:
                sup = super(ObjectModel, self)
                res = sup.horizontal_header_data(section)
        return res

