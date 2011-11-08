#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from functools import total_ordering

from traits.api import Event, HasTraits, ReadOnly

from ..enums import DataRole, ItemFlags, Match, Sorted


#-------------------------------------------------------------------------------
# ModelIndex
#-------------------------------------------------------------------------------
@total_ordering
class ModelIndex(object):
    """ ModelIndexes are used to navigate an AbstractItemModel.

    A ModelIndex is a lightweight object and should be created on the
    fly, rather than attempting some form of caching.

    """
    __slots__ = ('row', 'column', 'context', 'model')

    def __init__(self, row=-1, column=-1, context=None, model=None):
        """ Construct a model index.

        Arguments
        ---------
        row : int, optional
            The row index represented by this index. Defaults to -1.

        column : int, optional
            The column index represented by this index. Defaults to -1.

        context : object, optional
            A user supplied object that aids in navigating the user's
            model. Defaults to None.

        model : AbstractItemModel, optional
            The model in which this index is active. This is typically
            supplied by the create_index method of the AbstractItemModel.

        """
        self.row = row
        self.column = column
        self.context = context
        self.model = model

    def __eq__(self, other):
        """ Returns True if this index is functionally equivalent to
        another. False otherwise.

        """
        if isinstance(other, ModelIndex):
            return (self.row == other.row and
                    self.column == other.column and
                    self.context == other.context and
                    self.model == other.model)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        """ Returns True if this index is functionally less than another.
        False otherwise.

        """
        if isinstance(other, ModelIndex):
            if self.row < other.row:
                return True
            if self.row == other.row:
                if self.column < other.column:
                    return True
                if self.column == other.column:
                    # Rich comparing the user's objects has the potential
                    # to throw a TypeError. Like when comparing a datetime
                    # to a non-datetime.
                    try:
                        if self.context < other.context:
                            return True
                    except TypeError:
                        return True
                    if self.context == other.context:
                        return self.model < other.model
        return False

    def parent(self):
        """ Returns the parent ModelIndex of this index.

        """
        return self.model.parent(self)

    def sibling(self, row, column):
        """ Returns the sibling ModelIndex of this index for the given
        row and column indexes.

        """
        if self.row == row and self.column == column:
            return self
        return self.model.index(row, column, self.model.parent(self))

    def child(self, row, column):
        """ Returns the child ModelIndex of this index for the given
        row and column indexes.

        """
        return self.model.index(row, column, self)

    def data(self, role=DataRole.DISPLAY):
        """ Returns the data for this index for the given role.

        """
        return self.model.data(self, role)

    def flags(self):
        """ Returns the flags for this index.

        """
        return self.model.flags(self)

    def is_valid(self):
        """ Returns True if the if the row and column indices are greater
        than zero and the model is not None. False otherwise.

        """
        return self.row >= 0 and self.column >= 0 and self.model is not None


#-------------------------------------------------------------------------------
# AbstractItemModel
#-------------------------------------------------------------------------------
class AbstractItemModel(HasTraits):
    """ An abstract model for supplying information to heierarchical
    widgets.

    """
    #: Fired by the begin_insert_columns method
    columns_about_to_be_inserted = Event

    #: Fired by the begin_move_columns method
    columns_about_to_be_moved = Event

    #: Fired by the begin_remove_columns method
    columns_about_to_be_removed = Event

    #: Fired by the end_insert_columns method
    columns_inserted = Event

    #: Fired by the end_move_columns method
    columns_moved = Event

    #: Fired by the end_remove_rows method
    columns_removed = Event

    #: Fired by the begin_insert_rows method
    rows_about_to_be_inserted = Event

    #: Fired by the begin_move_rows method
    rows_about_to_be_moved = Event

    #: Fired by the begin_remove_columns method
    rows_about_to_be_removed = Event

    #: Fired by the end_insert_rows method
    rows_inserted = Event

    #: Fired by the end_move_rows method
    rows_moved = Event

    #: Fired by the end_remove_rows method
    rows_removed = Event

    #: Fired by the begin_change_layout method
    layout_about_to_be_changed = Event

    #: Fired by the end_change_layout method
    layout_changed = Event

    #: Fired by the begin_reset_model method
    model_about_to_be_reset = Event

    #: Fired by the end_reset_model method
    model_reset = Event

    #: Fired by the notify_data_changed method
    data_changed = Event

    #: Fired by the notify_header_data_changed method
    header_data_changed = Event

    def begin_insert_columns(self, parent, first, last):
        """ Begins inserting a column.

        This method must be called before inserting data into
        the model.

        Arguments
        ---------
        parent : ModelIndex
            The parent into which the new columns will be inserted.

        first : int
            The column position at which insertion will begin.

        last : int
            The column position at which insertion will end.

        """
        self.columns_about_to_be_inserted = True

    def begin_move_columns(self, source_parent, source_first, source_last,
                           destination_parent, destination_child):
        """ Begins to move a column.

        Arguments
        ---------
        source_parent : ModelIndex
            The item from which columns will be moved.

        source_first : int
            The number of the first column to be moved.

        source_last : int
            The number of the last column to be moved.

        destination_parent : ModelIndex
            The item into which the columns will be moved.

        destination_child : int
            The column number to which the columns will be moved.

        """
        self.columns_about_to_be_moved = True

    def begin_remove_columns(self, parent, first, last):
        """ Begins to remove columns.

        This method must be called before removing data from the
        model.

        Arguments
        ---------
        parent : ModelIndex
            The item from which the columns will be removed.

        first : int
            The number of the first column to remove.

        last : int
            The number of the last column to remove.

        """
        self.columns_about_to_be_removed = True

    def end_insert_columns(self):
        """ Finish inserting columns.

        This method must be called after inserting data into
        the model.

        """
        self.columns_inserted = True

    def end_move_columns(self):
        """ Finish moving columns.

        This method must be called after moving data in a model.

        """
        self.columns_moved = True

    def end_remove_columns(self):
        """ Finish removing columns.

        This method must be called after removing data from a model.

        """
        self.columns_removed = True

    def begin_insert_rows(self, parent, first, last):
        """ Begins a row insertion.

        This method must be called before inserting data into
        the model.

        Arguments
        ---------
        parent : ModelIndex
            The item into which the new rows will be inserted.

        first : int
            The row position at which insertion will begin.

        last : int
            The row position at which insertion will end.

        """

        self.rows_about_to_be_inserted = True

    def begin_move_rows(self, source_parent, source_first, source_last,
                        destination_parent, destination_child):
        """ Begins to move a row.

        Arguments
        ---------
        source_parent : ModelIndex
            The item from which rows will be moved.

        source_first : int
            The number of the first row to be moved.

        source_last : int
            The number of the last row to be moved.

        destination_parent : ModelIndex
            The item into which the rows will be moved.

        destination_child : int
            The row number to which the rows will be moved.

        """
        self.rows_about_to_be_moved = True

    def begin_remove_rows(self, parent, first, last):
        """ Begins to remove rows.

        This method must be called before removing data from the
        model.

        Arguments
        ---------
        parent : ModelIndex
            The item from which the rows will be removed.

        first : int
            The number of the first row to remove.

        last : int
            The number of the last row to remove.

        """
        self.rows_about_to_be_removed = True

    def end_insert_rows(self):
        """ Finish inserting rows.

        This method must be called after inserting data into
        the model.

        """
        self.rows_inserted = True

    def end_move_rows(self):
        """ Finish moving rows

        This method must be called after moving data in a model.

        """
        self.rows_moved = True

    def end_remove_rows(self):
        """ Finish removing rows.

        This method must be called after moving data in a model.

        """
        self.rows_removed = True

    def begin_change_layout(self):
        """ Begin a change to the layout of the model -- e.g., sort it.

        This method must be called before rearranging data in a model.

        """
        self.layout_about_to_be_changed = True

    def end_change_layout(self):
        """ Finish a change to the layout of the model.

        This method must be called after rearrangin data in a model.

        """
        self.layout_changed = True

    def begin_reset_model(self):
        """ Begin to reset a model.

        Model indices must be recomputed, and any associated
        views will also reset.

        This method must be called before a model is reset.

        """
        self.model_about_to_be_reset = True

    def end_reset_model(self):
        """ Finish resetting a model.

        This method must be called after a model is reset.

        """
        self.model_reset = True

    def buddy(self, index):
        """ Refers the caller to an item in the model to edit.

        Each item is its own buddy by default, but this is not required.

        Arguments
        ---------
        index : ModelIndex
            The model index for which a buddy will

        Returns
        -------
        buddy : ModelIndex
            The item that should be edited.

        """
        return index

    def can_fetch_more(self, parent):
        """ Returns `True` if itmes of `parent` can provide more data.

        Arguments
        ---------
        parent : ModelIndex
            A model item, possibly with more data that can be fetched.

        Returns
        -------
        has_more : bool
            True if more data is available, False otherwise.

        """
        return False

    def fetch_more(self, parent):
        """ Obtain data from model items, if more is available.

        This method is useful when incrementally adding data to a model.

        Arguments
        ---------
        parent : ModelIndex
            An index to query.

        Returns
        -------
        data : AbstractItemModel
            Data that has yet to be received.

        """
        pass

    def has_index(self, row, column, parent=ModelIndex()):
        """ Determine whether this model can provide a valid index with
        certain specifications.

        Arguments
        ---------
        row : int
            A row to be used in the index.

        column : int
            A column to be used in the index.

        parent : ModelIndex, optional
            A parent on which to base the new model index.

        Returns
        -------
        result : bool
            True if the inputs produce a valid index, False otherwise.

        """
        if row < 0 or column < 0:
            return False
        return row < self.row_count(parent) and column < self.column_count(parent)

    def has_children(self, parent=ModelIndex()):
        """ Determines if an index has any child items.

        Arguments
        ---------
        parent : ModelIndex, optional
            A model index to check for children.

        Returns
        -------
        result : bool
            True if the index has children, False otherwise.

        """
        return self.row_count(parent) > 0 and self.column_count(parent) > 0

    def create_index(self, row, column, context):
        """ Create a new index into this model.

        Arguments
        ---------
        row : int
            A row to specify the index

        column : int
            A column to specify the index.

        context : object
            A value that can be useful when working with a model.

        Returns
        -------
        index : ModelIndex
            A new index into this model.

        """
        return ModelIndex(row, column, context, self)

    def notify_data_changed(self, top_left, bottom_right):
        """ Create a notification that model data has changed.

        Arguments
        ---------
        top_left : ModelIndex
            The upper-left boundary of the changed items.

        bottom_right : ModelIndex
            The bottom-right boundary of the changed items.

        """
        self.data_changed = (top_left, top_right)

    def notify_header_data_changed(self, orientation, first, last):
        """ Create a notification that model header data has changed.

        Arguments
        ---------
        orientation : str
            Specify if changed the header is ``vertical`` or
            ``horizontal``.

        first : int
            The first column or row header that has been modified.

        last : int
            The last column or row header that has been modified.

        """
        self.header_data_changed = (orientation, first, last)

    def flags(self, index):
        """ Obtain the flags that specify user interaction with items.

        Arguments
        ---------
        index : ModelIndex
            Items to query.

        Returns
        -------
        item_flags : enaml.enums.ItemFlags
            The ways in which a view can interact with the items.

        """
        if not index.is_valid():
            return 0
        return ItemFlags.IS_SELECTABLE | ItemFlags.IS_ENABLED

    def header_data(self, section, orientation, role=DataRole.DISPLAY):
        """ Get data from a header, possibly specifying the data role.

        Arguments
        ---------
        section : int
            The row or column number of a header.

        orientation : str
            Select a ``horizontal`` header or a ``vertical`` header.

        role : enaml.enums.DataRole
            Select data with a particular role.

        Returns
        -------
        data : Any
            The requested data.

        """
        if role == DataRole.DISPLAY:
            return section + 1

    def item_data(self, index):
        """ Get a mapping of the form {DataRole: value} for each data
        role defined on the given item.

        Arguments
        ---------
        index : ModelIndex
            An item from which to obtain data.

        Returns
        -------
        data : Dict(enaml.enums.DataRole, Any)
            The requested data.

        """
        res = {}
        for role in DataRole.ALL:
            res[role] = self.data(index, role)
        return res

    def match(self, start, role, value, hits=1,
              flags=Match.STARTS_WITH | Match.WRAP):
        """ Search along an axis for data matching a particular value.

        Arguments
        ---------
        start : int
            A row or column at which to begin the search.

        role : enaml.enums.DataRole
            A data role to check in the search.

        value : Any
            The sought-after result.

        hits : int
            The maximum number of matches.

        flags : enaml.enums.Match
            Options to customize the search.

        Returns
        -------
        matches : List(ModelIndex)
            An index for each item that matched.

        """
        pass

    def set_data(self, index, value, role=DataRole.EDIT):
        """ Update a model item's data.

        Arguments
        ---------
        index : ModelIndex
            An item to update.

        value : Any
            A new value.

        role : enaml.enums.DataRole
            The data role to modify.

        Returns
        -------
        success : bool
            True if the data was successfully set, False otherwise.

        """
        return False

    def set_header_data(self, section, orientation, value, role=DataRole.EDIT):
        """ Update a header's data.

        Arguments
        ---------
        section : int
            The row or column of a header.

        orientation : str
            The axis along which the update will occur.

        value : Any
            A new value.

        role : enaml.enums.DataRole
            The data role to modify.

        Returns
        -------
        success : bool
            True if the header data was updated, False otherwise.

        """
        return False

    def set_item_data(self, index, roles):
        """ Update an item's data, for certain data roles.

        Arguments
        ---------
        index : ModelIndex
            An item to update.

        roles : Dict(enaml.enums.DataRole, Any)
            A map of data roles to their associated new values.

        Returns
        -------
        success : bool
            True if the data was updated succesfully, False otherwise.
        """
        res = True
        for role, value in roles.iteritems():
            res &= self.dat_data(index, value, role)
        return res

    def sibling(self, row, column, index):
        """ Obtain an item with the same parent as `index`.

        Arguments
        ---------
        row : int
            The row of the new item.

        column : int
            The column of the new item.

        index : ModelIndex
            An item for which to find a "sibling".

        Returns
        -------
        index : ModelIndex
            An element with the same parent as the specified item.

        """
        return self.index(row, column, self.parent(index))

    def sort(self, column, order=Sorted.ASCENDING):
        """ Sort the model by values in a column.

        Arguments
        ---------
        column : int
            The column on which to sort.

        order : enaml.enums.Sorted
            The ordering of the sort.

        """
        pass

    #---------------------------------------------------------------------------
    # Abstract Methods
    #---------------------------------------------------------------------------
    def column_count(self, parent=ModelIndex()):
        """ Count the number of columns in the children of an item.

        Arguments
        ---------
        parent : ModelIndex
            A model item with children.

        Returns
        -------
        count : int
            The number of columns in the model.

        """
        raise NotImplementedError

    def row_count(self, parent=ModelIndex()):
        """ Count the number of rows in the children of an item.

        Arguments
        ---------
        parent : ModelIndex
            A model item with children.

        Returns
        -------
        count : int
            The number of rows in the model.

        """
        raise NotImplementedError

    def index(self, row, column, parent=ModelIndex()):
        """ Obtain an index coresponding to an item in the model.

        Arguments
        ---------
        row : int
            The sought-after item's row.

        column : int
            The sought-after item's column.

        parent : ModelIndex
            The parent item that is the base of this index.

        Returns
        -------
        item : ModelIndex
            An index for the specified item.

        """
        raise NotImplementedError

    def parent(self, index):
        """ Obtain the parent of a model item.

        Arguments
        ---------
        index : ModelIndex
            A model item, possibly with a valid parent.

        Returns
        -------
        index : ModelIndex
            An index for the parent item.

        """
        raise NotImplementedError

    def data(self, index, role=DataRole.DISPLAY):
        """ Get a model item's data, for a particular role.

        Arguments
        ---------
        index : ModelIndex
            An item to query.

        Returns
        -------
        value : Any
            The requested value.

        """
        raise NotImplementedError


#-------------------------------------------------------------------------------
# AbstractTableModel
#-------------------------------------------------------------------------------
class AbstractTableModel(AbstractItemModel):

    def index(self, row, column, parent=ModelIndex()):
        if self.has_index(row, column, parent):
            return self.create_index(row, column, None)
        return ModelIndex()

    def parent(self, index):
        return ModelIndex()

    def has_children(self, parent=ModelIndex()):
        if parent.model() is self or not parent.is_valid():
            return self.row_count(parent) > 0 and self.column_count(parent) > 0
        return False


#-------------------------------------------------------------------------------
# AbstractListModel
#-------------------------------------------------------------------------------
class AbstractListModel(AbstractItemModel):

    def index(self, row, column, parent=ModelIndex()):
        if self.has_index(row, column, parent):
            return self.create_index(row, column, None)
        return ModelIndex()

    def parent(self, index):
        return ModelIndex()

    def column_count(self, parent=ModelIndex()):
        if parent.is_valid():
            return 0
        return 1

    def has_children(self, parent=ModelIndex()):
        if parent.is_valid():
            return False
        return self.row_count() > 0


#-------------------------------------------------------------------------------
# DispatchMixin
#-------------------------------------------------------------------------------
class DispatchMixin(HasTraits):

    _data_dispatch_table = ReadOnly

    _header_dispatch_table = ReadOnly

    def __data_dispatch_table_default(self):
        table = {
            DataRole.DISPLAY: self.data_display,
            DataRole.DECORATION: self.data_decoration,
            DataRole.EDIT: self.data_edit,
            DataRole.TOOL_TIP: self.data_tool_tip,
            DataRole.STATUS_TIP: self.data_status_tip,
            DataRole.WHATS_THIS: self.data_whats_this,
            DataRole.FONT: self.data_font,
            DataRole.TEXT_ALIGNMENT: self.data_text_alignment,
            DataRole.BACKGROUND: self.data_background,
            DataRole.FOREGROUND: self.data_foreground,
            DataRole.CHECK_STATE: self.data_check_state,
            DataRole.SIZE_HINT: self.data_size_hint,
            DataRole.USER: self.data_user,
        }
        return table

    def __header_dispatch_table_default(self):
        table = {
            DataRole.DISPLAY: self.header_display,
            DataRole.DECORATION: self.header_decoration,
            DataRole.EDIT: self.header_edit,
            DataRole.TOOL_TIP: self.header_tool_tip,
            DataRole.STATUS_TIP: self.header_status_tip,
            DataRole.WHATS_THIS: self.header_whats_this,
            DataRole.FONT: self.header_font,
            DataRole.TEXT_ALIGNMENT: self.header_text_alignment,
            DataRole.BACKGROUND: self.header_background,
            DataRole.FOREGROUND: self.header_foreground,
            DataRole.CHECK_STATE: self.header_check_state,
            DataRole.SIZE_HINT: self.header_size_hint,
            DataRole.USER: self.header_user,
        }
        return table

    #---------------------------------------------------------------------------
    # Data dispatching
    #---------------------------------------------------------------------------
    def data(self, index, role=DataRole.DISPLAY):
        return self._data_dispatch_table[role](index)

    def data_display(self, index):
        pass

    def data_decoration(self, index):
        pass

    def data_edit(self, index):
        pass

    def data_tool_tip(self, index):
        pass

    def data_status_tip(self, index):
        pass

    def data_whats_this(self, index):
        pass

    def data_font(self, index):
        pass

    def data_text_alignment(self, index):
        pass

    def data_background(self, index):
        pass

    def data_foreground(self, index):
        pass

    def data_check_state(self, index):
        pass

    def data_size_hint(self, index):
        pass

    def data_user(self, index):
        pass

    #---------------------------------------------------------------------------
    # Header dispatching
    #---------------------------------------------------------------------------
    def header_data(self, section, orientation, role=DataRole.DISPLAY):
        return self._header_dispatch_table(section, orientation)

    def header_display(self, section, orientation):
        return section + 1

    def header_decoration(self, section, orientation):
        pass

    def header_edit(self, section, orientation):
        pass

    def header_tool_tip(self, section, orientation):
        pass

    def header_status_tip(self, section, orientation):
        pass

    def header_whats_this(self, section, orientation):
        pass

    def header_font(self, section, orientation):
        pass

    def header_text_alignment(self, section, orientation):
        pass

    def header_background(self, section, orientation):
        pass

    def header_foreground(self, section, orientation):
        pass

    def header_check_state(self, section, orientation):
        pass

    def header_size_hint(self, section, orientation):
        pass

    def header_user(self, section, orientation):
        pass

