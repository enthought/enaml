#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt, QAbstractTableModel
from .qt.QtGui import QTableView
from .qt_control import QtControl
from .qt_font_utils import QtFontCache
from .qt_widget import q_parse_color


class QItemModelWrapper(QAbstractTableModel):

    role_handlers = {
        Qt.DisplayRole: '_item_display_role',
        Qt.DecorationRole: '_item_decoration_role',
        Qt.EditRole: '_item_edit_role',
        Qt.ToolTipRole: '_item_tool_tip_role',
        Qt.StatusTipRole: '_item_status_tip_role',
        Qt.FontRole: '_item_font_role',
        Qt.TextAlignmentRole: '_item_text_alignment_role',
        Qt.BackgroundRole: '_item_background_role',
        Qt.ForegroundRole: '_item_foreground_role',
        Qt.CheckStateRole: '_item_check_state_role',
        Qt.SizeHintRole: '_item_size_hint_role',
    }

    def __init__(self, model):
        super(QItemModelWrapper, self).__init__()
        self._model = model
        self._colors = {}
        self._fonts = QtFontCache()
        model.data_changed.connect(self._on_data_changed)
        model.model_changed.connect(self._on_model_changed)

    def _on_data_changed(self, row, column):
        index = self.index(row, column)
        self.dataChanged.emit(index, index)

    def _on_model_changed(self):
        self.beginResetModel()
        self.endResetModel()

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return self._model.row_count()

    def columnCount(self, parent):
        if parent.isValid():
            return 0
        return self._model.column_count()

    def flags(self, index):
        return Qt.ItemFlags(self._model.flags(index.row(), index.column()))

    def data(self, index, role):
        handler = self.role_handlers[role]
        return getattr(self, handler)(index.row(), index.column())

    def setData(self, index, value, role):
        row = index.row()
        column = index.column()
        if role == Qt.EditRole:
            return self._model.set_data(row, column, value)
        if role == Qt.CheckStateRole:
            return self._model.set_check_state(row, column, value)
        return False

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _item_display_role(self, row, column):
        return self._model.data(row, column)

    def _item_decoration_role(self, row, column):
        return None

    def _item_edit_role(self, row, column):
        return self._model.edit_data(row, column)

    def _item_tool_tip_role(self, row, column):
        return self._model.tool_tip(row, column)

    def _item_status_tip_role(self, row, column):
        return self._model.status_tip(row, column)

    def _item_font_role(self, row, column):
        font = self._model.font(row, column)
        if font:
            return self._fonts[font]

    def _item_text_alignment_role(self, row, column):
        return Qt.Alignment(self._model.text_alignment(row, column))

    def _item_background_role(self, row, column):
        color = self._model.background(row, column)
        if color:
            colors = self._colors
            if color in colors:
                qcolor = colors[color]
            else:
                qcolor = colors[color] = q_parse_color(color)
            return qcolor

    def _item_foreground_role(self, row, column):
        color = self._model.foreground(row, column)
        if color:
            colors = self._colors
            if color in colors:
                qcolor = colors[color]
            else:
                qcolor = colors[color] = q_parse_color(color)
            return qcolor

    def _item_check_state_role(self, row, column):
        state = self._model.check_state(row, column)
        if state is not None:
            return Qt.CheckState(state)

    def _item_size_hint_role(self, row, column):
        return None


class QtItemView(QtControl):
    """ A Qt implementation of an Enaml ItemsView.

    """
    def create_widget(self, parent, tree):
        widget = QTableView(parent)
        #widget.horizontalHeader().setVisible(False)
        widget.verticalHeader().setDefaultSectionSize(20)
        #widget.verticalHeader().setVisible(False)
        widget.setShowGrid(False)
        widget.viewport().setAttribute(Qt.WA_StaticContents, True)
        widget.setHorizontalScrollMode(widget.ScrollPerPixel)
        widget.setVerticalScrollMode(widget.ScrollPerPixel)
        return widget

    def create(self, tree):
        super(QtItemView, self).create(tree)
        self.set_item_model(tree['item_model'])
        self.widget().resizeColumnsToContents()

    def set_item_model(self, model):
        self.widget().setModel(QItemModelWrapper(model))

