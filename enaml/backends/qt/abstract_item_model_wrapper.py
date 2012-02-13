#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import itertools
import operator

from .qt.QtCore import Qt, QAbstractItemModel, QModelIndex
from .styling import q_color_from_color, q_font_from_font

from ...item_models.abstract_item_model import AbstractItemModel


#: An invalid QModelIndex() for use in conversion routines
_INVALID_QINDEX = QModelIndex()


#------------------------------------------------------------------------------
# Flag Map
#------------------------------------------------------------------------------
# The construction cost of creating an ItemsFlag object is very high
# so instead we enumerate all 128 combinations so we can look them 
# up as a simple map. This is a hack to workaround a PySide issue
# where it doesn't accept ints as return values from the flags() method
_qitem_flags = (
    Qt.NoItemFlags, Qt.ItemIsSelectable, Qt.ItemIsEditable,
    Qt.ItemIsDragEnabled, Qt.ItemIsDropEnabled, Qt.ItemIsUserCheckable,
    Qt.ItemIsEnabled, Qt.ItemIsTristate,
)


_QITEM_FLAGS = {}


for n in range(1, len(_qitem_flags) + 1):
    for items in itertools.combinations(_qitem_flags, n):
        val = reduce(operator.or_, items, 0)
        _QITEM_FLAGS[int(val)] = val


del _qitem_flags


#------------------------------------------------------------------------------
# Role Mapping Builders
#------------------------------------------------------------------------------
def _build_getters(model):
    """ Returns a dictionary of role->getter methods for the given
    model.

    """
    return {
        int(Qt.DisplayRole): model.data,
        int(Qt.DecorationRole): model.decoration,
        int(Qt.EditRole): model.edit_data,
        int(Qt.ToolTipRole): model.tool_tip,
        int(Qt.StatusTipRole): model.status_tip,
        int(Qt.WhatsThisRole): model.whats_this,
        int(Qt.FontRole): model.font,
        int(Qt.TextAlignmentRole): model.alignment,
        int(Qt.BackgroundRole): model.background,
        int(Qt.ForegroundRole): model.foreground,
        int(Qt.CheckStateRole): model.check_state,
        int(Qt.SizeHintRole): model.size_hint,
        int(Qt.UserRole): lambda *args, **kwargs: None,
    }


def _build_setters(model):
    """ Returns a dictionary of role->setter methods for the given
    model.

    """
    return {
        int(Qt.DisplayRole): model.set_data,
        int(Qt.EditRole): model.set_data,
        int(Qt.CheckStateRole): model.set_check_state,
    }


def _build_h_header_getters(model):
    """ Returns a dictionary of role->h_header getter methods for the
    given model.

    """
    return {
        int(Qt.DisplayRole): model.horizontal_header_data,
        int(Qt.DecorationRole): model.horizontal_header_decoration,
        int(Qt.ToolTipRole): model.horizontal_header_tool_tip,
        int(Qt.StatusTipRole): model.horizontal_header_status_tip,
        int(Qt.WhatsThisRole): model.horizontal_header_whats_this,
        int(Qt.FontRole): model.horizontal_header_font,
        int(Qt.TextAlignmentRole): model.horizontal_header_alignment,
        int(Qt.BackgroundRole): model.horizontal_header_background,
        int(Qt.ForegroundRole): model.horizontal_header_foreground,
        int(Qt.SizeHintRole): model.horizontal_header_size_hint,
        int(Qt.UserRole): lambda *args, **kwargs: None,
    }


def _build_v_header_getters(model):
    """ Returns a dictionary of role->v_header getter methods for the
    given model.

    """
    return {
        int(Qt.DisplayRole): model.vertical_header_data,
        int(Qt.DecorationRole): model.vertical_header_decoration,
        int(Qt.ToolTipRole): model.vertical_header_tool_tip,
        int(Qt.StatusTipRole): model.vertical_header_status_tip,
        int(Qt.WhatsThisRole): model.vertical_header_whats_this,
        int(Qt.FontRole): model.vertical_header_font,
        int(Qt.TextAlignmentRole): model.vertical_header_alignment,
        int(Qt.BackgroundRole): model.vertical_header_background,
        int(Qt.ForegroundRole): model.vertical_header_foreground,
        int(Qt.SizeHintRole): model.vertical_header_size_hint,
        int(Qt.UserRole): lambda *args, **kwargs: None,
    }


#------------------------------------------------------------------------------
# Data Converters
#------------------------------------------------------------------------------
def _not_yet_supported(val):
    # use this converter for roles that are not 
    # yet supported.
    return None


def _no_convert(val):
    # These values don't need converting because they should
    # come from the user model with a Qt compatible type.
    return val


def _brush_convert(brush):
    # We don't yet support a full brush, so for now just 
    # return the color. Which works fine.
    if brush:
        return q_color_from_color(brush.color)


# Some of these should be LRU cached    
def _font_convert(font):
    if font:
        return q_font_from_font(font)


_QROLE_CONVERTERS = {
    int(Qt.DisplayRole): _no_convert,
    int(Qt.DecorationRole): _not_yet_supported,
    int(Qt.EditRole): _no_convert,
    int(Qt.ToolTipRole): _no_convert,
    int(Qt.StatusTipRole): _no_convert,
    int(Qt.WhatsThisRole): _no_convert,
    int(Qt.FontRole): _font_convert,
    int(Qt.TextAlignmentRole): _no_convert,
    int(Qt.BackgroundRole): _brush_convert,
    int(Qt.ForegroundRole): _brush_convert,
    int(Qt.CheckStateRole): _not_yet_supported,
    int(Qt.SizeHintRole): _no_convert,
    int(Qt.UserRole): _not_yet_supported,
}


#------------------------------------------------------------------------------
# AbstractItemModelWrapper
#------------------------------------------------------------------------------
class AbstractItemModelWrapper(QAbstractItemModel):
    """ A QAbstractItemModel subclass which wraps an instance of an
    Enaml AbstractItemModel and does the appropriate delegation and
    conversion between Python and Qt

    """
    def __init__(self, item_model):
        super(AbstractItemModelWrapper, self).__init__()
        if not isinstance(item_model, AbstractItemModel):
            raise TypeError('Model must be an instance of AbstractItemModel.')
        
        self._item_model = item_model
        self._getters = _build_getters(item_model)
        self._setters = _build_setters(item_model)
        self._h_header_getters = _build_h_header_getters(item_model)
        self._v_header_getters = _build_v_header_getters(item_model)

        def listen(name):
            signal = getattr(item_model, name)
            signal.connect(getattr(self, '_' + name))

        listen('columns_about_to_be_inserted')
        listen('columns_about_to_be_moved')
        listen('columns_about_to_be_removed')
        listen('columns_inserted')
        listen('columns_moved')
        listen('columns_removed')

        listen('rows_about_to_be_inserted')
        listen('rows_about_to_be_moved')
        listen('rows_about_to_be_removed')
        listen('rows_inserted')
        listen('rows_moved')
        listen('rows_removed')

        listen('layout_about_to_be_changed')
        listen('layout_changed')

        listen('model_about_to_be_reset')
        listen('model_reset')
        listen('data_changed')
        listen('horizontal_header_data_changed')
        listen('vertical_header_data_changed')

    #--------------------------------------------------------------------------
    # Traits Event Handlers
    #--------------------------------------------------------------------------
    def _columns_about_to_be_inserted(self, evt_arg):
        parent, start, end = evt_arg
        q_index = self.to_q_index(parent)
        self.columnsAboutToBeInserted.emit(q_index, start, end)
    
    def _columns_about_to_be_moved(self, evt_arg):
        parent, start, end = evt_arg
        q_index = self.to_q_index(parent)
        self.columnsAboutToBeMoved.emit(q_index, start, end)
    
    def _columns_about_to_be_removed(self, evt_arg):
        parent, start, end = evt_arg
        q_index = self.to_q_index(parent)
        self.columnsAboutToBeRemoved.emit(q_index, start, end)
    
    def _columns_inserted(self, evt_arg):
        parent, start, end = evt_arg
        q_index = self.to_q_index(parent)
        self.columnsInserted.emit(q_index, start, end)
    
    def _columns_moved(self, evt_arg):
        parent, start, end = evt_arg
        q_index = self.to_q_index(parent)
        self.columnsMoved.emit(q_index, start, end)
    
    def _columns_removed(self, evt_arg):
        parent, start, end = evt_arg
        q_index = self.to_q_index(parent)
        self.columnsRemoved.emit(q_index, start, end)

    def _rows_about_to_be_inserted(self, evt_arg):
        parent, start, end = evt_arg
        q_index = self.to_q_index(parent)
        self.rowsAboutToBeInserted.emit(q_index, start, end)
    
    def _rows_about_to_be_moved(self, evt_arg):
        parent, start, end = evt_arg
        q_index = self.to_q_index(parent)
        self.rowsAboutToBeMoved.emit(q_index, start, end)
    
    def _rows_about_to_be_removed(self, evt_arg):
        parent, start, end = evt_arg
        q_index = self.to_q_index(parent)
        self.rowsAboutToBeRemoved.emit(q_index, start, end)
    
    def _rows_inserted(self, evt_arg):
        parent, start, end = evt_arg
        q_index = self.to_q_index(parent)
        self.rowsInserted.emit(q_index, start, end)
    
    def _rows_moved(self, evt_arg):
        parent, start, end = evt_arg
        q_index = self.to_q_index(parent)
        self.rowsMoved.emit(q_index, start, end)
    
    def _rows_removed(self, evt_arg):
        parent, start, end = evt_arg
        q_index = self.to_q_index(parent)
        self.rowsRemoved.emit(q_index, start, end)
    
    def _layout_about_to_be_changed(self):
        self.layoutAboutToBeChanged.emit()
    
    def _layout_changed(self):
        self.layoutChanged.emit()
            
    def _model_about_to_be_reset(self):
        self.modelAboutToBeReset.emit()
    
    def _model_reset(self):
        self.modelReset.emit()
    
    def _data_changed(self, evt_arg):
        top_left, bottom_right = evt_arg
        q_top_left = self.to_q_index(top_left)
        q_bottom_right = self.to_q_index(bottom_right)
        self.dataChanged.emit(q_top_left, q_bottom_right)
    
    def _horizontal_header_data_changed(self, evt_arg):
        first, last = evt_arg
        self.headerDataChanged.emit(Qt.Horizontal, first, last)

    def _vertical_header_data_changed(self, evt_arg):
        first, last = evt_arg
        self.headerDataChanged.emit(Qt.Vertical, first, last)
    
    #--------------------------------------------------------------------------
    # AbstractItemModel interface 
    #--------------------------------------------------------------------------
    def buddy(self, index):
        enaml_index = self.from_q_index(index)
        enaml_buddy = self._item_model.buddy(enaml_index)
        return self.to_q_index(enaml_buddy)

    def canFetchMore(self, parent):
        enaml_parent = self.from_q_index(parent)
        return self._item_model.can_fetch_more(enaml_parent)

    def fetchMore(self, parent):
        enaml_parent = self.from_q_index(parent)
        return self._item_model.fetchMore(enaml_parent)
        
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal:
            res = self._h_header_getters[role](section)
        else:
            res = self._v_header_getters[role](section)
        return res

    def setData(self, index, value, role):
        enaml_index = self.from_q_index(index)
        setter = self._setters.get(role)
        if setter is not None:
            res = setter(enaml_index, value)
        else:
            res = False
        return res
        
    def flags(self, index):
        enaml_index = self.from_q_index(index)
        enaml_flags = self._item_model.flags(enaml_index)
        return _QITEM_FLAGS[enaml_flags]

    def rowCount(self, parent):
        enaml_index = self.from_q_index(parent)
        return self._item_model.row_count(enaml_index)

    def columnCount(self, parent):
        enaml_index = self.from_q_index(parent)
        return self._item_model.column_count(enaml_index)
    
    def index(self, row, column, parent):
        enaml_parent = self.from_q_index(parent)
        enaml_index = self._item_model.index(row, column, enaml_parent)
        return self.to_q_index(enaml_index)
    
    def parent(self, index):
        enaml_index = self.from_q_index(index)
        enaml_parent = self._item_model.parent(enaml_index)
        return self.to_q_index(enaml_parent)

    def data(self, index, role):
        enaml_index = self.from_q_index(index)
        if enaml_index is None:
            return
        data = self._getters[role](enaml_index)
        return _QROLE_CONVERTERS[role](data)

    # XXX we don't have a use case at the moment for setHeaderData
    def setHeaderData(self, section, orientation, value, role):
       return False
    
    def from_q_index(self, q_index):
        if not q_index.isValid():
            return None
        row = q_index.row()
        col = q_index.column()
        context = q_index.internalPointer()
        return self._item_model.create_index(row, col, context)

    def to_q_index(self, enaml_index):
        if enaml_index is None:
            return _INVALID_QINDEX
        row = enaml_index.row
        col = enaml_index.column
        context = enaml_index.context
        return self.createIndex(row, col, context)

