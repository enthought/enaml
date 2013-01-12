#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.qt.qt.QtCore import Qt
from enaml.qt.qt.QtGui import QFrame

from .tabular_model import NullModel


class QTabularHeader(QFrame):

    def __init__(self, orientation, parent=None):
        super(QTabularHeader, self).__init__(parent)
        assert orientation in (Qt.Horizontal, Qt.Vertical)
        self._orientation = orientation
        self._model = NullModel()

    def orientation(self):
        return self._orientation

    def model(self):
        return self._model

    def setModel(self, model):
        self._model = model

    def count(self):
        if self._orientation == Qt.Horizontal:
            c = self._model.column_count()
        else:
            c = self._model.row_count()
        return c

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    def length(self):
        raise NotImplementedError

    def offset(self):
        raise NotImplementedError

    def setOffset(self, offset):
        raise NotImplementedError

    def visualIndexAt(self, position):
        raise NotImplementedError

    def logicalIndexAt(self, position):
        raise NotImplementedError

    def visualIndex(self, logical_index):
        raise NotImplementedError

    def logicalIndex(self, visual_index):
        raise NotImplementedError

    def sectionSize(self, visual_index):
        raise NotImplementedError

    def sectionPosition(self, visual_index):
        raise NotImplementedError



class QFixedSizeHeader(QTabularHeader):

    def __init__(self, orientation, parent=None):
        super(QFixedSizeHeader, self).__init__(orientation, parent)
        if self.orientation() == Qt.Horizontal:
            self._section_size = 50
        else:
            self._section_size = 17
        self._offset = 0

    def length(self):
        return self._section_size * self.count()

    def offset(self):
        return self._offset

    def setOffset(self, offset):
        self._offset = offset

    def visualIndexAt(self, position):
        virtual = position + self._offset
        return virtual / self._section_size

    def logicalIndexAt(self, position):
        return self.visualIndexAt(position)

    def visualIndex(self, logical_index):
        return logical_index

    def logicalIndex(self, visual_index):
        return visual_index

    def sectionSize(self, visual_index):
        return self._section_size

    def sectionPosition(self, visual_index):
        return visual_index * self._section_size - self._offset

