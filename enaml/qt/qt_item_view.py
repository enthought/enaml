#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from enaml.modelview.enums import ItemDataRole

from .qt.QtCore import Qt, QAbstractTableModel
from .qt.QtGui import QTableView
from .qt_control import QtControl
from .qt_font_utils import QtFontCache
from .qt_widget import q_parse_color


class QItemModelWrapper(QAbstractTableModel):

    role_handlers = {
        Qt.DisplayRole: (ItemDataRole.DISPLAY_ROLE, '_item_data'),
        Qt.DecorationRole: (ItemDataRole.DECORATION_ROLE, '_item_decoration'),
        Qt.EditRole: (ItemDataRole.EDIT_ROLE, '_item_data'),
        Qt.ToolTipRole: (ItemDataRole.TOOL_TIP_ROLE, '_item_data'),
        Qt.StatusTipRole: (ItemDataRole.STATUS_TIP_ROLE, '_item_data'),
        Qt.FontRole: (ItemDataRole.FONT_ROLE, '_item_font'),
        Qt.TextAlignmentRole: (ItemDataRole.TEXT_ALIGNMENT_ROLE, '_item_text_alignment'),
        Qt.BackgroundRole: (ItemDataRole.BACKGROUND_ROLE, '_item_color'),
        Qt.ForegroundRole: (ItemDataRole.FOREGROUND_ROLE, '_item_color'),
        Qt.CheckStateRole: (ItemDataRole.CHECK_STATE_ROLE, '_item_check_state'),
        Qt.SizeHintRole: (ItemDataRole.SIZE_HINT_ROLE, '_item_size_hint'),
    }

    def __init__(self, model):
        super(QItemModelWrapper, self).__init__()
        self._model = model
        self._colors = {}
        self._fonts = QtFontCache()

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def flags(self, index):
        row = index.row()
        column = index.column()
        return Qt.ItemFlags(self._model.item_flags(row, column))

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return self._model.row_count()

    def columnCount(self, parent):
        if parent.isValid():
            return 0
        return self._model.column_count()

    def data(self, index, role):
        enaml_role, handler = self.role_handlers[role]
        return getattr(self, handler)(index.row(), index.column(), enaml_role)

    def setData(self, index, value, role):
        row = index.row()
        column = index.column()
        if role == Qt.EditRole:
            enaml_role = ItemDataRole.EDIT_ROLE
            return self._model.set_item_data(row, column, value, enaml_role)
        if role == Qt.CheckStateRole:
            enaml_role = ItemDataRole.CHECK_STATE_ROLE
            return self._model.set_item_data(row, column, value, enaml_role)
        return False

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _item_data(self, row, column, role):
        return self._model.item_data(row, column, role)

    def _item_decoration(self, row, column, role):
        return None

    def _item_font(self, row, column, role):
        font = self._model.item_data(row, column, role)
        if font:
            return self._fonts[font]

    def _item_text_alignment(self, row, column, role):
        alignment = self._model.item_data(row, column, role)
        if alignment is not None:
            return Qt.Alignment(alignment)

    def _item_color(self, row, column, role):
        color = self._model.item_data(row, column, role)
        if color:
            colors = self._colors
            if color in colors:
                qcolor = colors[color]
            else:
                qcolor = colors[color] = q_parse_color(color)
            return qcolor

    def _item_check_state(self, row, column, role):
        state = self._model.item_data(row, column, role)
        if state is not None:
            return Qt.CheckState(state)

    def _item_size_hint(self, row, column, role):
        return None


class QtItemView(QtControl):
    """ A Qt implementation of an Enaml ItemsView.

    """
    def create_widget(self, parent, tree):
        widget = QTableView(parent)
        widget.horizontalHeader().setVisible(False)
        widget.verticalHeader().setVisible(False)
        #widget.setShowGrid(False)
        #widget.viewport().setAttribute(Qt.WA_StaticContents, True)
        #widget.setHorizontalScrollMode(widget.ScrollPerPixel)
        return widget

    def create(self, tree):
        super(QtItemView, self).create(tree)
        self.set_item_model(tree['item_model'])

    def set_item_model(self, model):
        self.widget().setModel(QItemModelWrapper(model))

