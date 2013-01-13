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

    ScrollPerPixel = 0
    ScrollPerItem = 1

    def __init__(self, parent=None):
        super(QTabularView, self).__init__(parent)
        self._model = NullModel()
        self._v_header = QFixedSizeHeader(Qt.Vertical)
        self._h_header = QFixedSizeHeader(Qt.Horizontal)
        self._h_scroll = QTabularView.ScrollPerPixel
        self._v_scroll = QTabularView.ScrollPerPixel
        viewport = self.viewport()
        viewport.setAttribute(Qt.WA_StaticContents, True)
        viewport.setAutoFillBackground(True)
        viewport.setFocusPolicy(Qt.ClickFocus)
        self.updateScrollBars()

    def updateScrollBars(self):
        v_header = self._v_header
        h_header = self._h_header
        v_bar = self.verticalScrollBar()
        h_bar = self.horizontalScrollBar()
        size = self.viewport().size()
        width = size.width()
        height = size.height()
        if self._v_scroll == QTabularView.ScrollPerPixel:
            v_bar.setRange(0, v_header.length() - height)
        else:
            s = v_header.sectionSize(0) # XXX fixed row height assumption
            v_bar.setRange(0, v_header.count() - height / s)
        if self._h_scroll == QTabularView.ScrollPerPixel:
            h_bar.setRange(0, h_header.length() - width)
        else:
            s = h_header.sectionSize(0) # XXX fixed col width assumption
            h_bar.setRange(0, h_header.count() - width / s)

    def model(self):
        return self._model

    def setModel(self, model):
        assert isinstance(model, TabularModel)
        self._model = model
        self._v_header.setModel(model)
        self._h_header.setModel(model)
        self.updateScrollBars()

    def horizontalScrollMode(self):
        return self._h_scroll

    def setHorizontalScrollMode(self, mode):
        valid = (QTabularView.ScrollPerPixel, QTabularView.ScrollPerItem)
        assert mode in valid
        self._h_scroll = mode

    def verticalScrollMode(self):
        return self._v_scroll

    def setVerticalScrollMode(self, mode):
        valid = (QTabularView.ScrollPerPixel, QTabularView.ScrollPerItem)
        assert mode in valid
        self._v_scroll = mode

    def resizeEvent(self, event):
        super(QTabularView, self).resizeEvent(event)
        self.updateScrollBars()

    def scrollContentsBy(self, dx, dy):
        if dx != 0:
            header = self._h_header
            old = header.offset()
            if self._h_scroll == QTabularView.ScrollPerPixel:
                new = self.horizontalScrollBar().value()
                header.setOffset(new)
            else:
                idx = header.visualIndexAt(0)
                nidx = max(0, min(idx - dx, header.lastVisualIndex()))
                header.setOffsetToVisualIndex(nidx)
                new = header.offset()
            dx = old - new
        if dy != 0:
            header = self._v_header
            old = header.offset()
            if self._v_scroll == QTabularView.ScrollPerPixel:
                new = self.verticalScrollBar().value()
                header.setOffset(new)
            else:
                idx = header.visualIndexAt(0)
                nidx = max(0, min(idx - dy, header.lastVisualIndex()))
                header.setOffsetToVisualIndex(nidx)
                new = header.offset()
            dy = old - new
        viewport = self.viewport()
        size = viewport.size()
        if abs(dx) >= size.width() or abs(dy) >= size.height():
            viewport.update()
        else:
            scrollWidget(viewport, dx, dy)

    def paintEvent(self, event):
        h_header = self._h_header
        v_header = self._v_header
        model = self._model

        if h_header.count() == 0 or v_header.count() == 0:
            return

        painter = QPainter(self.viewport())
        dr = QRect()
        dl = QLine()

        for rect in event.region().rects():
            painter.setClipRect(rect)

            x1 = rect.x()
            x2 = x1 + rect.width()
            y1 = rect.y()
            y2 = y1 + rect.height()

            first_visual_row = v_header.visualIndexAt(y1)
            last_visual_row = v_header.visualIndexAt(y2)
            first_visual_col = h_header.visualIndexAt(x1)
            last_visual_col = h_header.visualIndexAt(x2)

            if first_visual_row == -1 or first_visual_col == -1:
                continue

            if last_visual_row == -1:
                last_visual_row = v_header.lastVisualIndex()
            if last_visual_col == -1:
                last_visual_col = h_header.lastVisualIndex()

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
                ndata = data.next
                for r_height in row_sizes:
                    xr = x
                    for c_width in col_sizes:
                        dr.setRect(xr, yr, c_width, r_height)
                        painter.drawText(dr, Qt.AlignCenter, str(ndata()))
                        xr += c_width
                    yr += r_height
            except StopIteration: # ran out of data early
                pass

            # Draw the grid lines
            painter.save()
            painter.setPen(Qt.gray)

            xm = xr
            ym = yr
            yr = y
            for r_height in row_sizes:
                dl.setLine(x1, yr, xm, yr)
                painter.drawLine(dl)
                yr += r_height
            dl.setLine(x1, yr, xm, yr)
            painter.drawLine(dl)

            xr = x
            for c_width in col_sizes:
                dl.setLine(xr, y1, xr, ym)
                painter.drawLine(dl)
                xr += c_width
            dl.setLine(xr, y1, xr, ym)

            painter.drawLine(dl)
            painter.restore()

