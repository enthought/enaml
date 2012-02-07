#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from .model_index import ModelIndex

from ..core.signaling import Signal


#------------------------------------------------------------------------------
# The various AbstractItemModel flags
#------------------------------------------------------------------------------
# Item flags (these are the same values as Qt's flags so we don't
# have to do a map lookup for Qt).
NO_ITEM_FLAGS = 0x0         # The item has no state flags
ITEM_IS_SELECTABLE = 0x1    # The item can be selected in a view.
ITEM_IS_EDITABLE = 0x2      # The item can be edited in a view.
ITEM_IS_DRAG_ENABLED = 0x4  # The item can be dragged.
ITEM_IS_DROP_ENABLED = 0x8  # Another item can be dropped onto this one.
ITEM_IS_CHECKABLE = 0x10    # The item's "checked" state can be changed from a view.
ITEM_IS_ENABLED = 0x20      # This item permits user interaction in a view.
ITEM_IS_TRISTATE = 0x40     # The item is checkable, and it has three distinct states.


# Alignment flags (these are the same values as Qt's flags so we don't
# have to do a map lookup for Qt).
ALIGN_LEFT = 0x1
ALIGN_RIGHT = 0x2
ALIGN_HCENTER = 0x4
ALIGN_JUSTIFY = 0x8
ALIGN_TOP = 0x20
ALIGN_BOTTOM = 0x40
ALIGN_VCENTER = 0x80
ALIGN_CENTER = ALIGN_HCENTER | ALIGN_VCENTER


#------------------------------------------------------------------------------
# AbstractItemModel
#------------------------------------------------------------------------------
class AbstractItemModel(object):
    """ An abstract model for supplying information to heierarchical
    widgets.

    """
    __metaclass__ = ABCMeta

    #: Fired by the begin_insert_columns method
    columns_about_to_be_inserted = Signal()

    #: Fired by the begin_move_columns method
    columns_about_to_be_moved = Signal()

    #: Fired by the begin_remove_columns method
    columns_about_to_be_removed = Signal()

    #: Fired by the end_insert_columns method
    columns_inserted = Signal()

    #: Fired by the end_move_columns method
    columns_moved = Signal()

    #: Fired by the end_remove_rows method
    columns_removed = Signal()

    #: Fired by the begin_insert_rows method
    rows_about_to_be_inserted = Signal()

    #: Fired by the begin_move_rows method
    rows_about_to_be_moved = Signal()

    #: Fired by the begin_remove_columns method
    rows_about_to_be_removed = Signal()

    #: Fired by the end_insert_rows method
    rows_inserted = Signal()

    #: Fired by the end_move_rows method
    rows_moved = Signal()

    #: Fired by the end_remove_rows method
    rows_removed = Signal()

    #: Fired by the begin_change_layout method
    layout_about_to_be_changed = Signal()

    #: Fired by the end_change_layout method
    layout_changed = Signal()

    #: Fired by the begin_reset_model method
    model_about_to_be_reset = Signal()

    #: Fired by the end_reset_model method
    model_reset = Signal()

    #: Fired by the notify_data_changed method
    data_changed = Signal()
    
    #: Fired by the notify_horizontal_header_data_changed method
    horizontal_header_data_changed = Signal()

    #: Fired by the notify_vertical_header_data_changed method
    vertical_header_data_changed = Signal()
    
    #--------------------------------------------------------------------------
    # Model change notification trigger methods 
    #--------------------------------------------------------------------------
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
        evt_arg = (parent, first, last)
        self.columns_about_to_be_inserted(evt_arg)

    def begin_move_columns(self, src_parent, src_first, src_last, dst_parent, dst_child):
        """ Begins to move a column.

        Arguments
        ---------
        src_parent : ModelIndex
            The item from which columns will be moved.

        src_first : int
            The number of the first column to be moved.

        src_last : int
            The number of the last column to be moved.

        dst_parent : ModelIndex
            The item into which the columns will be moved.

        dst_child : int
            The column number to which the columns will be moved.

        """
        evt_arg = (src_parent, src_first, src_last, dst_parent, dst_child)
        self.columns_about_to_be_moved(evt_arg)

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
        evt_arg = (parent, first, last)
        self.columns_about_to_be_removed(evt_arg)

    def end_insert_columns(self, parent, first, last):
        """ Finish inserting columns.

        This method must be called after inserting data into
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
        evt_arg = (parent, first, last)
        self.columns_inserted(evt_arg)

    def end_move_columns(self, src_parent, src_first, src_last, dst_parent, dst_child):
        """ Finish moving columns.

        This method must be called after moving data in a model.

        Arguments
        ---------
        src_parent : ModelIndex
            The item from which columns will be moved.

        src_first : int
            The number of the first column to be moved.

        src_last : int
            The number of the last column to be moved.

        dst_parent : ModelIndex
            The item into which the columns will be moved.

        dst_child : int
            The column number to which the columns will be moved.

        """
        evt_arg = (src_parent, src_first, src_last, dst_parent, dst_child)
        self.columns_moved(evt_arg)

    def end_remove_columns(self, parent, first, last):
        """ Finish removing columns.

        This method must be called after removing data from a model.

        Arguments
        ---------
        parent : ModelIndex
            The item from which the columns will be removed.

        first : int
            The number of the first column to remove.

        last : int
            The number of the last column to remove.

        """
        evt_arg = (parent, first, last)
        self.columns_removed(evt_arg)

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
        evt_arg = (parent, first, last)
        self.rows_about_to_be_inserted(evt_arg)

    def begin_move_rows(self, src_parent, src_first, src_last,
                        dst_parent, dst_child):
        """ Begins to move a row.

        Arguments
        ---------
        src_parent : ModelIndex
            The item from which rows will be moved.

        src_first : int
            The number of the first row to be moved.

        src_last : int
            The number of the last row to be moved.

        dst_parent : ModelIndex
            The item into which the rows will be moved.

        dst_child : int
            The row number to which the rows will be moved.

        """
        evt_arg = (src_parent, src_first, src_last, dst_parent, dst_child)
        self.rows_about_to_be_moved(evt_arg)

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
        evt_arg = (parent, first, last)
        self.rows_about_to_be_removed(evt_arg)

    def end_insert_rows(self, parent, first, last):
        """ Finish inserting rows.

        This method must be called after inserting data into
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
        evt_arg = (parent, first, last)
        self.rows_inserted(evt_arg)

    def end_move_rows(self, src_parent, src_first, src_last, dst_parent, dst_child):
        """ Finish moving rows

        This method must be called after moving data in a model.

        Arguments
        ---------
        src_parent : ModelIndex
            The item from which rows will be moved.

        src_first : int
            The number of the first row to be moved.

        src_last : int
            The number of the last row to be moved.

        dst_parent : ModelIndex
            The item into which the rows will be moved.

        dst_child : int
            The row number to which the rows will be moved.

        """
        evt_arg = (src_parent, src_first, src_last, dst_parent, dst_child)
        self.rows_moved(evt_arg)

    def end_remove_rows(self, parent, first, last):
        """ Finish removing rows.

        This method must be called after moving data in a model.

        Arguments
        ---------
        parent : ModelIndex
            The item from which the rows will be removed.

        first : int
            The number of the first row to remove.

        last : int
            The number of the last row to remove.

        """
        evt_arg = (parent, first, last)
        self.rows_removed(evt_arg)

    def begin_change_layout(self):
        """ Begin a change to the layout of the model -- e.g., sort it.

        This method must be called before rearranging data in a model.

        """
        self.layout_about_to_be_changed()

    def end_change_layout(self):
        """ Finish a change to the layout of the model.

        This method must be called after rearranging data in a model.

        """
        self.layout_changed()

    def begin_reset_model(self):
        """ Begin to reset a model.

        Model indices must be recomputed, and any associated views will 
        also be reset.

        This method must be called before a model is reset.

        """
        self.model_about_to_be_reset()

    def end_reset_model(self):
        """ Finish resetting a model.

        This method must be called after a model is reset.

        """
        self.model_reset()

    def notify_data_changed(self, top_left, bottom_right):
        """ Create a notification event for the model data has changed.

        Arguments
        ---------
        top_left : ModelIndex
            The upper-left boundary of the changed items.

        bottom_right : ModelIndex
            The bottom-right boundary of the changed items.

        """
        self.data_changed((top_left, bottom_right))

    def notify_horizontal_header_data_changed(self, first, last):
        """ Create a notification that model horizontal header data 
        has changed.

        Arguments
        ---------
        first : int
            The first horizontal/column header that has been modified.

        last : int
            The last horizontal/column header that has been modified.

        """
        self.horizontal_header_data_changed((first, last))

    def notify_vertical_header_data_changed(self, first, last):
        """ Create a notification that model vertical header data 
        has changed.

        Arguments
        ---------
        first : int
            The first vertical/row header that has been modified.

        last : int
            The last vertical/row header that has been modified.

        """
        self.vertical_header_data_changed((first, last))

    #--------------------------------------------------------------------------
    # Misc methods 
    #--------------------------------------------------------------------------
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

    def buddy(self, index):
        """ Refers the caller to an item in the model to edit.

        Each item is its own buddy by default, but this is not required.

        Arguments
        ---------
        index : ModelIndex
            The model index for which the buddy index should be 
            returned for editing.

        Returns
        -------
        buddy : ModelIndex
            The item that should be edited.

        """
        return index

    def can_fetch_more(self, parent=None):
        """ Returns `True` if items of `parent` can provide more data.

        Arguments
        ---------
        parent : ModelIndex or None
            A model index, possibly with more data that can be fetched.

        Returns
        -------
        has_more : bool
            True if more data is available, False otherwise.

        """
        return False

    def fetch_more(self, parent=None):
        """ Obtain data from model items, if more is available.

        This method is useful when incrementally adding data to a model.

        Arguments
        ---------
        parent : ModelIndex or None
            An index to query.

        Returns
        -------
        data : AbstractItemModel
            Data that has yet to be received.

        """
        pass

    def has_index(self, row, column, parent=None):
        """ Determine whether this model can provide a valid index with
        certain specifications.

        Arguments
        ---------
        row : int
            A row to be used in the index.

        column : int
            A column to be used in the index.

        parent : ModelIndex or None
            A parent on which to base the new model index.

        Returns
        -------
        result : bool
            True if the inputs produce a valid index, False otherwise.

        """
        if row < 0 or column < 0:
            return False
        return row < self.row_count(parent) and column < self.column_count(parent)

    def has_children(self, parent=None):
        """ Determines if an index has any child items.

        Arguments
        ---------
        parent : ModelIndex or None
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

    def flags(self, index):
        """ Obtain the flags that specify user interaction with items.

        Arguments
        ---------
        index : ModelIndex
            Items to query.

        Returns
        -------
        item_flags : tuple of strings
            The ways in which a view can interact with the items.

        """
        return ITEM_IS_SELECTABLE | ITEM_IS_ENABLED

    #--------------------------------------------------------------------------
    # Abstract Methods
    #--------------------------------------------------------------------------
    @abstractmethod
    def column_count(self, parent=None):
        """ Count the number of columns in the children of an item.

        Arguments
        ---------
        parent : ModelIndex or None
            A model item with children.

        Returns
        -------
        count : int
            The number of columns in the model.

        """
        raise NotImplementedError

    @abstractmethod
    def row_count(self, parent=None):
        """ Count the number of rows in the children of an item.

        Arguments
        ---------
        parent : ModelIndex or None
            A model item with children.

        Returns
        -------
        count : int
            The number of rows in the model.

        """
        raise NotImplementedError

    @abstractmethod
    def index(self, row, column, parent=None):
        """ Obtain an index coresponding to an item in the model.

        Arguments
        ---------
        row : int
            The sought-after item's row.

        column : int
            The sought-after item's column.

        parent : ModelIndex or None
            The parent item that is the base of this index.

        Returns
        -------
        item : ModelIndex or None
            An index for the specified item.

        """
        raise NotImplementedError

    @abstractmethod
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


    @abstractmethod
    def data(self, index):
        """ Get the data for a model index as a string for display.

        Arguments
        ---------
        index : ModelIndex
            The model index for which to return the data.

        Returns
        -------
        value : string
            The data as a string for display.

        """
        raise NotImplementedError

    #--------------------------------------------------------------------------
    # Auxiliary Data Methods
    #--------------------------------------------------------------------------
    def decoration(self, index):
        """ Return an icon for the index

        The default implementation returns None.

        Arguments
        ---------
        index : ModelIndex
            The model index for which to return the icon.

        Returns
        -------
        value : icon??
            The icon to display for the cell.

        """
        # XXX Handle Icons !!!
        return None
    
    def edit_data(self, index):
        """ Get the data for a model index as a string for editing.

        The default implementation returns 'data(index)'.

        Arguments
        ---------
        index : ModelIndex
            The model index for which to return the data.

        Returns
        -------
        value : string
            The data as a string for editing.

        """
        return self.data(index)
    
    def tool_tip(self, index):
        """ Get the tool tip string for a given model index.

        The default implementation returns None.

        Arguments
        ---------
        index : ModelIndex
            The model index for which to return the tool tip.

        Returns
        -------
        value : string
            The tool tip string.

        """
        return None
    
    def status_tip(self, index):
        """ Get the status tip string for a given model index.

         The default implementation returns None.

        Arguments
        ---------
        index : ModelIndex
            The model index for which to return the status tip.

        Returns
        -------
        value : string
            The status tip string.

        """
        return None

    def whats_this(self, index):
        """ Get the what's this? string for a given model index.

         The default implementation returns None.

        Arguments
        ---------
        index : ModelIndex
            The model index for which to return the what's this? string.

        Returns
        -------
        value : string
            The what's this? string.

        """
        return None
    
    def font(self, index):
        """ Get the font for a given model index.

        The default implementation returns None.

        Arguments
        ---------
        index : ModelIndex
            The model index for which to return the font.

        Returns
        -------
        value : Font
            The font to use for this model index.

        """
        return None
    
    def alignment(self, index):
        """ Get the alignment of the text for a given model index.

        The default implementation returns ALIGN_VCENTER | ALIGN_RIGHT

        Arguments
        ---------
        index : ModelIndex
            The model index for which to return the alignment.

        Returns
        -------
        value : int
            The OR'd alignment flags to use for the given model index.

        """
        return ALIGN_VCENTER | ALIGN_RIGHT
    
    def background(self, index):
        """ The background brush to use for the given index.

        The default implementation returns None.

        Arguments
        ---------
        index : ModelIndex
            The model index for which to return the brush.

        Returns
        -------
        value : Brush
            The brush to use for the given model index.

        """
        return None
    
    def foreground(self, index):
        """ The foreground brush to use for the given index.

        The default implementation returns None.

        Arguments
        ---------
        index : ModelIndex
            The model index for which to return the brush.

        Returns
        -------
        value : Brush
            The brush to use for the given model index.

        """
        return None
    
    def check_state(self, index):
        """ Get the check state for the given index.

        The default implementation returns None.

        Arguments
        ---------
        index : ModelIndex
            The model index for which to return the check state.

        Returns
        -------
        value : string
            The check state to use for the given model index.

        """
        return None
    
    def size_hint(self, index):
        """ Get the (width, height) size hint for the given index.

        The default implementation returns None.

        Arguments
        ---------
        index : ModelIndex
            The model index for which to return the size hint.

        Returns
        -------
        value : (width, height)
            The size hint to use for the given model index.

        """
        return None

    #--------------------------------------------------------------------------
    # Data Setter Methods
    #--------------------------------------------------------------------------
    def set_data(self, index, value):
        """ Update a model item's data. The default implementation does
        nothing and returns False.

        Implementations that allow editing must set the 'editable' flag
        to True, and call notify_data_changed(...) explicity in order
        for the table to update.

        Arguments
        ---------
        index : ModelIndex
            The model index for the item to update.

        value : object
            The user supplied value to set in the model.

        Returns
        -------
        success : bool
            True if the data was successfully set, False otherwise.

        """
        return False
    
    def set_check_state(self, index, value):
        """ Update a model item's check state. The default implementation 
        does nothing and returns False.

        Implementations that allow editing must set the 'editable' flag
        to True, and call notify_data_changed(...) explicity in order
        for the table to update.

        Arguments
        ---------
        index : ModelIndex
            The model index for the item to update.

        value : object
            The check state to set in the model.

        Returns
        -------
        success : bool
            True if the data was successfully set, False otherwise.

        """
        return False
    
    #--------------------------------------------------------------------------
    # Header Data Methods 
    #--------------------------------------------------------------------------
    def horizontal_header_data(self, section):
        """ Get the horizontal label for a particular header section.

        The default implementation returns the column number of the given 
        header. Subclasses should override this method to return 
        appropriate data for their model.

        Arguments
        ---------
        section : int
            The column number of the header.

        Returns
        -------
        data : string
            The requested header label

        """
        return unicode(section + 1)
    
    def vertical_header_data(self, section):
        """ Get the vertical label for a particular header section.

        The default implementation returns the row number of the given 
        header. Subclasses should override this method to return 
        appropriate data for their model.

        Arguments
        ---------
        section : int
            The row number of the header.

        Returns
        -------
        data : string
            The requested header label

        """
        return unicode(section + 1)

    #--------------------------------------------------------------------------
    # Header Data auxiliary methods
    #--------------------------------------------------------------------------
    def horizontal_header_decoration(self, section):
        """ Get the horizontal icon for a particular header section.

        The default implementation returns None.

        Arguments
        ---------
        section : int
            The column number of the header.

        Returns
        -------
        data : icon??
            The requested icon for the header

        """
        # XXX implement icons
        return None
    
    def vertical_header_decoration(self, section):
        """ Get the vertical icon for a particular header section.

        The default implementation returns None.

        Arguments
        ---------
        section : int
            The row number of the header.

        Returns
        -------
        data : icon??
            The requested icon for the header

        """
        # XXX implement icons
        return None

    def horizontal_header_tool_tip(self, section):
        """ Get the horizontal tool tip for a particular header section.

        The default implementation returns None.

        Arguments
        ---------
        section : int
            The column number of the header.

        Returns
        -------
        data : string
            The requested tool tip for the header

        """
        return None
    
    def vertical_header_tool_tip(self, section):
        """ Get the vertical tool tip for a particular header section.

        The default implementation returns None.

        Arguments
        ---------
        section : int
            The row number of the header.

        Returns
        -------
        data : string
            The requested tool tip for the header

        """
        return None   
    
    def horizontal_header_status_tip(self, section):
        """ Get the horizontal status tip for a particular header section.

        The default implementation returns None.

        Arguments
        ---------
        section : int
            The column number of the header.

        Returns
        -------
        data : string
            The requested status tip for the header

        """
        return None
    
    def vertical_header_status_tip(self, section):
        """ Get the vertical status tip for a particular header section.

        The default implementation returns None.

        Arguments
        ---------
        section : int
            The row number of the header.

        Returns
        -------
        data : string
            The requested status tip for the header

        """
        return None 
        
    def horizontal_header_whats_this(self, section):
        """ Get the horizontal whats this for a particular header section.

        The default implementation returns None.

        Arguments
        ---------
        section : int
            The column number of the header.

        Returns
        -------
        data : string
            The requested what's this? for the header

        """
        return None
    
    def vertical_header_whats_this(self, section):
        """ Get the vertical whats this for a particular header section.

        The default implementation returns None.

        Arguments
        ---------
        section : int
            The row number of the header.

        Returns
        -------
        data : string
            The requested what's this? for the header

        """
        return None 
    
    def horizontal_header_font(self, section):
        """ Get the horizontal font for a particular header section.

        The default implementation returns None.

        Arguments
        ---------
        section : int
            The column number of the header.

        Returns
        -------
        data : Font()
            The requested font for the header

        """
        return None
    
    def vertical_header_font(self, section):
        """ Get the vertical font for a particular header section.

        The default implementation returns None.

        Arguments
        ---------
        section : int
            The row number of the header.

        Returns
        -------
        data : Font()
            The requested font for the header

        """
        return None 

    def horizontal_header_alignment(self, section):
        """ Get the horizontal whats this for a particular header section.

        The default implementation returns ALIGN_CENTER.

        Arguments
        ---------
        section : int
            The column number of the header.

        Returns
        -------
        data : int
            The OR'd alignment flags for the header

        """
        return ALIGN_CENTER
    
    def vertical_header_alignment(self, section):
        """ Get the vertical whats this for a particular header section.

        The default implementation returns ALIGN_CENTER

        Arguments
        ---------
        section : int
            The row number of the header.

        Returns
        -------
        data : int
            The OR'd alignment flags for the header

        """
        return ALIGN_CENTER
    
    def horizontal_header_background(self, section):
        """ Get the horizontal background brush for a particular 
        header section.

        The default implementation returns None.

        Arguments
        ---------
        section : int
            The column number of the header.

        Returns
        -------
        data : Brush()
            The requested brush for the header

        """
        return None
    
    def vertical_header_background(self, section):
        """ Get the vertical background brush for a particular
        header section.

        The default implementation returns None.

        Arguments
        ---------
        section : int
            The row number of the header.

        Returns
        -------
        data : Brush()
            The requested brush for the header

        """
        return None 

    def horizontal_header_foreground(self, section):
        """ Get the horizontal foreground brush for a particular 
        header section.

        The default implementation returns None.

        Arguments
        ---------
        section : int
            The column number of the header.

        Returns
        -------
        data : Brush()
            The requested brush for the header

        """
        return None
    
    def vertical_header_foreground(self, section):
        """ Get the vertical foreground brush for a particular
        header section.

        The default implementation returns None.

        Arguments
        ---------
        section : int
            The row number of the header.

        Returns
        -------
        data : Brush()
            The requested brush for the header

        """
        return None

    def horizontal_header_size_hint(self, section):
        """ Get the horizontal size hint for a particular header section.

        The default implementation returns None.

        Arguments
        ---------
        section : int
            The column number of the header.

        Returns
        -------
        data : int
            The requested size hint for the width of the header.

        """
        return None
    
    def vertical_header_size_hint(self, section):
        """ Get the vertical size hint for a particular header section.

        The default implementation returns None.

        Arguments
        ---------
        section : int
            The column number of the header.

        Returns
        -------
        data : int
            The requested size hint for the height of the header.

        """
        return None

    #--------------------------------------------------------------------------
    # Header Data Setters
    #--------------------------------------------------------------------------
    
    # At the moment we dont have a compelling use case where we
    # need to be able to set the header data from the ui. But in 
    # the future, that functionality will be added here.


#------------------------------------------------------------------------------
# AbstractTableModel
#------------------------------------------------------------------------------
class AbstractTableModel(AbstractItemModel):
    """ An AbstractItemModel subclass that implements the methods 
    necessary to restrict the model to a 2-dimensional table of data.

    """
    def index(self, row, column, parent=None):
        """ Abstract method implementation that will create a valid
        model index for the given row and column if they are valid.
        Otherwise, returns an invalid index.

        """
        if self.has_index(row, column, parent):
            return self.create_index(row, column, None)

    def parent(self, index):
        """ Abstract method implementation that always returns None, 
        forcing the model to be flat.

        """
        return None

    def has_children(self, parent):
        """ Overridden parent class method which restrics the model to
        2-dimensions.

        """
        if parent is None or parent.model is self:
            return self.row_count(parent) > 0 and self.column_count(parent) > 0
        return False


#------------------------------------------------------------------------------
# AbstractListModel
#------------------------------------------------------------------------------
class AbstractListModel(AbstractItemModel):
    """ An AbstractItemModel subclass that implements the methods 
    necessary to restrict the model to a 1-dimensional list of data.

    """
    def index(self, row, column, parent=None):
        """ Abstract method implementation that will create a valid
        model index for the given row and column if they are valid.
        Otherwise, returns an invalid index.

        """
        if self.has_index(row, column, parent):
            return self.create_index(row, column, None)

    def parent(self, index):
        """ Abstract method implementation that always returns an
        invalid index, forcing the model to be flat.

        """
        return None

    def column_count(self, parent=None):
        """ Overridden parent class method which restricts the model
        to a single column.

        """
        if parent is not None:
            return 0
        return 1

    def has_children(self, parent=None):
        """ Overridden parent class method which restrics the model
        to 1-dimension.

        """
        if parent is not None:
            return False
        return self.row_count() > 0

