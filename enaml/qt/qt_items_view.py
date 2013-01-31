#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt, QAbstractTableModel, QVariant
from .qt.QtGui import QTableView
from .qt_control import QtControl
from .qt_widget import q_parse_color

class QItemsModelWrapper(QAbstractTableModel):

    def __init__(self, model):
        super(QItemsModelWrapper, self).__init__()
        self._model = model
        self._colors = {}
        self._fonts = {}

    def _lookupEditor(self, index):
        model_index = index.column()
        item_index = index.row()
        return self._model.editor(item_index, model_index - 1)

    def _lookupItem(self, index):
        item_index = index.row()
        return self._model.item(item_index)

    def _initEditor(self, editor):
        flags = Qt.NoItemFlags
        if editor.enabled:
            flags |= Qt.ItemIsEnabled
        if editor.selectable:
            flags |= Qt.ItemIsSelectable
        if editor.checkable:
            flags |= Qt.ItemIsUserCheckable
        if editor.editable:
            flags |= Qt.ItemIsEditable
        editor._toolkit_data = flags

    def flags(self, index):
        editor = self._lookupEditor(index)
        if editor is not None:
            tk_data = editor._toolkit_data
            if tk_data is None:
                self._initEditor(editor)
                tk_data = editor._toolkit_data
            return tk_data#['flags']
        return Qt.NoItemFlags

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return self._model.item_count()

    def columnCount(self, parent):
        if parent.isValid():
            return 0
        return self._model.model_count() + 1

    def _itemData(self, index, role):
        item = self._lookupItem(index)
        if item is None:
            return
        res = None
        if role == Qt.DisplayRole or role == Qt.EditRole:
            res = item.name
        elif role == Qt.ForegroundRole:
            color = item.foreground
            if not color:
                p = item.parent
                if p is not None:
                    color = p.foreground
            if color:
                if color not in self._colors:
                    res = self._colors[color] = q_parse_color(color)
                else:
                    res = self._colors[color]
        elif role == Qt.BackgroundRole:
            color = item.background
            if not color:
                p = item.parent
                if p is not None:
                    color = p.background
            if color:
                if color not in self._colors:
                    res = self._colors[color] = q_parse_color(color)
                else:
                    res = self._colors[color]
        return res

    def data(self, index, role):
        if index.column() == 0:
            return self._itemData(index, role)
        editor = self._lookupEditor(index)
        if editor is None:
            return
        res = None
        if role == Qt.DisplayRole or role == Qt.EditRole:
            res = editor.value
        elif role == Qt.ForegroundRole:
            color = editor.foreground
            if color:
                if color not in self._colors:
                    res = self._colors[color] = q_parse_color(color)
                else:
                    res = self._colors[color]
        elif role == Qt.BackgroundRole:
            color = editor.background
            if color:
                if color not in self._colors:
                    res = self._colors[color] = q_parse_color(color)
                else:
                    res = self._colors[color]
        return res

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            item_index = index.row()
            model_index = index.column()
            if model_index > 0:
                editor = self._model.editor(item_index, model_index - 1)
                if editor is not None:
                    editor.value = value
                    self.dataChanged.emit(index, index)
                    return True
        return False


class QtItemsView(QtControl):
    """ A Qt implementation of an Enaml ItemsView.

    """
    def create_widget(self, parent, tree):
        widget = QTableView(parent)
        widget.horizontalHeader().setVisible(False)
        widget.verticalHeader().setVisible(False)
        #widget.viewport().setAttribute(Qt.WA_StaticContents, True)
        widget.setHorizontalScrollMode(widget.ScrollPerPixel)
        return widget

    def create(self, tree):
        super(QtItemsView, self).create(tree)
        self.set_items_model(tree['items_model'])

    def set_items_model(self, model):
        self.widget().setModel(QItemsModelWrapper(model))