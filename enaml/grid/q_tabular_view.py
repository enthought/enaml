#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys


from enaml.qt.qt.QtCore import Qt, QRect, QLine
from enaml.qt.qt.QtGui import QPainter, QAbstractScrollArea

from .tabular_model import TabularModel, NullModel
from .q_abstract_header import QFixedSizeHeader

# Qt::WA_StaticContents is broken on OSX. QWidget::scroll also appears
# to not work entirely correctly and overdraws part of the buffer. On
# that platform, the whole widget must be fully repainted on scroll.
# According to the Qt bug tracker, this was fixed in version 4.8
# I've yet to test it on that version though...
if sys.platform == 'darwin':
    scrollWidget = lambda widget, dx, dy: widget.update()
else:
    scrollWidget = lambda widget, dx, dy: widget.scroll(dx, dy)



class QTabularView(QAbstractScrollArea):

    def __init__(self, parent=None):
        super(QTabularView, self).__init__(parent)
        self._model = NullModel()
        self._v_header = QFixedSizeHeader(Qt.Vertical)
        self._h_header = QFixedSizeHeader(Qt.Horizontal)
        viewport = self.viewport()
        viewport.setAttribute(Qt.WA_StaticContents, True)
        viewport.setAutoFillBackground(True)
        viewport.setFocusPolicy(Qt.ClickFocus)
        self.updateScrollBars()

    def updateScrollBars(self):
        size = self.viewport().size()
        vrange = self._v_header.length()
        hrange = self._h_header.length()
        self.verticalScrollBar().setRange(0, vrange - size.height())
        self.horizontalScrollBar().setRange(0, hrange - size.width())

    def model(self):
        return self._model

    def setModel(self, model):
        assert isinstance(model, TabularModel)
        self._model = model
        self._v_header.setModel(model)
        self._h_header.setModel(model)
        self.updateScrollBars()

    def resizeEvent(self, event):
        super(QTabularView, self).resizeEvent(event)
        self.updateScrollBars()

    def scrollContentsBy(self, dx, dy):
        if dx != 0:
            header = self._h_header
            old = header.offset()
            new = self.horizontalScrollBar().value()
            header.setOffset(new)
            dx = old - new
        if dy != 0:
            header = self._v_header
            old = header.offset()
            new = self.verticalScrollBar().value()
            header.setOffset(new)
            dy = old - new
        self.viewport().scroll(dx, dy)

    def paintEvent(self, event):
        h_header = self._h_header
        v_header = self._v_header
        model = self._model

        if h_header.count() == 0 or v_header.count() == 0:
            return
        max_x = h_header.length()
        max_y = v_header.length()

        painter = QPainter(self.viewport())
        dr = QRect()
        dl = QLine()
        print event.region().rects()
        for rect in event.region().rects():

            x1 = rect.x()
            x2 = x1 + rect.width()
            y1 = rect.y()
            y2 = y1 + rect.height()

            if x1 > max_x or y1 > max_y:
                continue

            first_visual_row = v_header.visualIndexAt(y1)
            last_visual_row = v_header.visualIndexAt(y2)
            first_visual_col = h_header.visualIndexAt(x1)
            last_visual_col = h_header.visualIndexAt(x2)

            if last_visual_row == -1:
                last_visual_row = v_header.lastVisualIndex()
            if last_visual_col == -1:
                last_visual_col = v_header.lastVisualIndex()

            row_sizes = []
            row_indices = []
            for idx in xrange(first_visual_row, last_visual_row + 1):
                row_sizes.append(v_header.sectionSize(idx))
                row_indices.append(v_header.logicalIndex(idx))

            col_sizes = []
            col_indices = []
            for idx in xrange(first_visual_col, last_visual_col + 1):
                col_sizes.append(h_header.sectionSize(idx))
                col_indices.append(h_header.logicalIndex(idx))

            # Draw the data
            data = iter(model.data(row_indices, col_indices))
            y = v_header.sectionPosition(first_visual_row)
            x = h_header.sectionPosition(first_visual_col)
            xr = x
            yr = y
            try:
                for r_height in row_sizes:
                    xr = x
                    for c_width in col_sizes:
                        dr.setRect(xr, yr, c_width, r_height)
                        painter.drawText(dr, Qt.AlignCenter, str(data.next()))
                        xr += c_width
                    yr += r_height
            except StopIteration:
                pass


            # Draw the grid lines
            painter.save()
            painter.setPen(Qt.gray)
            xm = x1 + sum(col_sizes)
            ym = y1 + sum(row_sizes)
            if y1 < ym:
                yr = y
                for r_height in row_sizes:
                    dl.setLine(x1, yr, xm, yr)
                    painter.drawLine(dl)
                    yr += r_height
            if x1 < xm:
                xr = x
                for c_width in col_sizes:
                    dl.setLine(xr, y1, xr, ym)
                    painter.drawLine(dl)
                    xr += c_width
            painter.restore()


