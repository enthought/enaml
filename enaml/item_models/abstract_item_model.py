from functools import total_ordering

from traits.api import Event, HasTraits, ReadOnly


#-------------------------------------------------------------------------------
# Role Flags
#-------------------------------------------------------------------------------
DISPLAY_ROLE = 0

DECORATION_ROLE = 1

EDIT_ROLE = 2

TOOL_TIP_ROLE = 3

STATUS_TIP_ROLE = 4

WHATS_THIS_ROLE = 5

FONT_ROLE = 6

TEXT_ALIGNMENT_ROLE = 7

BACKGROUND_ROLE = 8

FOREGROUND_ROLE = 9

CHECK_STATE_ROLE = 10

SIZE_HINT_ROLE = 11

USER_ROLE = 12

# XXX - HACK!
ALL_ROLES = tuple(range(12))


#-------------------------------------------------------------------------------
# Item Flags
#-------------------------------------------------------------------------------
NO_ITEM_FLAGS = 0

ITEM_IS_SELECTABLE = 1

ITEM_IS_EDITABLE = 2

ITEM_IS_DRAG_ENABLED = 4

ITEM_IS_DROP_ENABLED = 8

ITEM_IS_USER_CHECKABLE = 16

ITEM_IS_ENABLED = 32

ITEM_IS_TRISTATE = 64


#-------------------------------------------------------------------------------
# Match Flags
#-------------------------------------------------------------------------------
MATCH_EXACTLY = 0

MATCH_FIXED_STRING = 8

MATCH_CONTAINS = 1

MATCH_STARTS_WITH = 2

MATCH_ENDS_WITH = 3

MATCH_CASE_SENSITIVE = 16

MATCH_REG_EXP = 4

MATCH_WILD_CARD = 5

MATCH_WRAP = 32

MATCH_RECURSIVE = 64

DEFAULT_MATCH = MATCH_STARTS_WITH | MATCH_WRAP


#-------------------------------------------------------------------------------
# Sorting Flags
#-------------------------------------------------------------------------------
ASCENDING_ORDER = 0

DESCENDING_ORDER = 1


#-------------------------------------------------------------------------------
# ModelIndex
#-------------------------------------------------------------------------------
@total_ordering
class ModelIndex(object):

    __slots__ = ('row', 'column', 'context', 'model')

    def __init__(self, row=-1, column=-1, context=None, model=None):
        self.row = row
        self.column = column
        self.context = context
        self.model = model

    def __eq__(self, other):
        if isinstance(other, ModelIndex):
            return (self.row == other.row and
                    self.column == other.column and
                    self.context == other.context and
                    self.model == other.model)
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
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
        return self.model.parent(self)

    def sibling(self, row, column):
        if self.row == row and self.column == column:
            return self
        return self.model.index(row, column, self.model.parent(self))

    def child(self, row, column):
        return self.model.index(row, column, self)

    def data(self, role=DISPLAY_ROLE):
        return self.model.data(self, role)

    def flags(self):
        return self.model.flags(self)
    
    def is_valid(self):
        return self.row >= 0 and self.column >= 0 and self.model is not None


#-------------------------------------------------------------------------------
# AbstractItemModel
#-------------------------------------------------------------------------------
class AbstractItemModel(HasTraits):
    """ An abstract model for supplying information to heierarchical
    widgets.

    """
    # Fired by the begin_insert_columns method
    columns_about_to_be_inserted = Event

    # Fired by the begin_move_columns method
    columns_about_to_be_moved = Event

    # Fired by the begin_remove_columns method
    columns_about_to_be_removed = Event

    # Fired by the end_insert_columns method
    columns_inserted = Event

    # Fired by the end_move_columns method
    columns_moved = Event

    # Fired by the end_remove_rows method
    columns_removed = Event

    # Fired by the begin_insert_rows method
    rows_about_to_be_inserted = Event

    # Fired by the begin_move_rows method
    rows_about_to_be_moved = Event

    # Fired by the begin_remove_columns method
    rows_about_to_be_removed = Event

    # Fired by the end_insert_rows method
    rows_inserted = Event

    # Fired by the end_move_rows method
    rows_moved = Event

    # Fired by the end_remove_rows method
    rows_removed = Event

    # Fired by the begin_change_layout method
    layout_about_to_be_changed = Event

    # Fired by the end_change_layout method
    layout_changed = Event
    
    # Fired by the begin_reset_model method
    model_about_to_be_reset = Event

    # Fired by the end_reset_model method
    model_reset = Event

    # Fired by the notify_data_changed method
    data_changed = Event

    # Fired by the notify_header_data_changed method
    header_data_changed = Event

    def begin_insert_columns(self, parent, first, last):
        self.columns_about_to_be_inserted = True
    
    def begin_move_columns(self, source_parent, source_first, source_last, 
                           destination_parent, destination_child):
        self.columns_about_to_be_moved = True

    def begin_remove_columns(self, parent, first, last):
        self.columns_about_to_be_removed = True

    def end_insert_columns(self):
        self.columns_inserted = True

    def end_move_columns(self):
        self.columns_moved = True
    
    def end_remove_columns(self):
        self.columns_removed = True
    
    def begin_insert_rows(self, parent, first, last):
        self.rows_about_to_be_inserted = True
    
    def begin_move_rows(self, source_parent, source_first, source_last,
                        destination_parent, destination_child):
        self.rows_about_to_be_moved = True

    def begin_remove_rows(self, parent, first, last):
        self.rows_about_to_be_removed = True

    def end_insert_rows(self):
        self.rows_inserted = True
    
    def end_move_rows(self):
        self.rows_moved = True
    
    def end_remove_rows(self):
        self.rows_removed = True

    def begin_change_layout(self):
        self.layout_about_to_be_changed = True
    
    def end_change_layout(self):
        self.layout_changed = True
    
    def begin_reset_model(self):
        self.model_about_to_be_reset = True

    def end_reset_model(self):
        self.model_reset = True

    def buddy(self, index):
        return index
    
    def can_fetch_more(self, parent):
        return False

    def fetch_more(self, parent):
        pass

    def has_index(self, row, column, parent=ModelIndex()):
        if row < 0 or column < 0:
            return False
        return row < self.row_count(parent) and column < self.column_count(parent)

    def has_children(self, parent=ModelIndex()):
        return self.row_count(parent) > 0 and self.column_count(parent) > 0

    def create_index(self, row, column, context):
        return ModelIndex(row, column, context, self)

    def notify_data_changed(self, top_left, top_right):
        self.data_changed = (top_left, top_right)

    def notify_header_data_changed(self, orientation, first, last):
        self.header_data_changed = (orientation, first, last)

    def flags(self, index):
        if not index.is_valid():
            return 0
        return ITEM_IS_SELECTABLE | ITEM_IS_ENABLED

    def header_data(self, section, orientation, role=DISPLAY_ROLE):
        if role == DISPLAY_ROLE:
            return section + 1

    def item_data(self, index):
        res = {}
        for role in ALL_ROLES:
            res[role] = self.data(index, role)
        return res

    def match(self, start, role, value, hits=1, flags=DEFAULT_MATCH):
        pass

    def set_data(self, index, value, role=EDIT_ROLE):
        return False
    
    def set_header_data(self, section, orientation, value, role=EDIT_ROLE):
        return False
    
    def set_item_data(self, index, roles):
        res = True
        for role, value in roles.iteritems():
            res &= self.dat_data(index, value, role)
        return res

    def sibling(self, row, column, index):
        return self.index(row, column, self.parent(index))

    def sort(self, column, order=ASCENDING_ORDER):
        pass

    #---------------------------------------------------------------------------
    # Abstract Methods
    #---------------------------------------------------------------------------
    def column_count(self, parent=ModelIndex()):
        raise NotImplementedError
    
    def row_count(self, parent=ModelIndex()):
        raise NotImplementedError

    def index(self, row, column, parent=ModelIndex()):
        raise NotImplementedError

    def parent(self, index):
        raise NotImplementedError
    
    def data(self, index, role=DISPLAY_ROLE):
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
            DISPLAY_ROLE: self.data_display,
            DECORATION_ROLE: self.data_decoration,
            EDIT_ROLE: self.data_edit,
            TOOL_TIP_ROLE: self.data_tool_tip,
            STATUS_TIP_ROLE: self.data_status_tip,
            WHATS_THIS_ROLE: self.data_whats_this,
            FONT_ROLE: self.data_font,
            TEXT_ALIGNMENT_ROLE: self.data_text_alignment,
            BACKGROUND_ROLE: self.data_background,
            FOREGROUND_ROLE: self.data_foreground,
            CHECK_STATE_ROLE: self.data_check_state,
            SIZE_HINT_ROLE: self.data_size_hint,
            USER_ROLE: self.data_user,
        }
        return table

    def __header_dispatch_table_default(self):
        table = {
            DISPLAY_ROLE: self.header_display,
            DECORATION_ROLE: self.header_decoration,
            EDIT_ROLE: self.header_edit,
            TOOL_TIP_ROLE: self.header_tool_tip,
            STATUS_TIP_ROLE: self.header_status_tip,
            WHATS_THIS_ROLE: self.header_whats_this,
            FONT_ROLE: self.header_font,
            TEXT_ALIGNMENT_ROLE: self.header_text_alignment,
            BACKGROUND_ROLE: self.header_background,
            FOREGROUND_ROLE: self.header_foreground,
            CHECK_STATE_ROLE: self.header_check_state,
            SIZE_HINT_ROLE: self.header_size_hint,
            USER_ROLE: self.header_user,
        }
        return table

    #---------------------------------------------------------------------------
    # Data dispatching
    #---------------------------------------------------------------------------
    def data(self, index, role=DISPLAY_ROLE):
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
    def header_data(self, section, orientation, role=DISPLAY_ROLE):
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

