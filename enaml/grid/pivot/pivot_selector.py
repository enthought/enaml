
from pyface.qt.QtCore import Qt, QRect, QSize, QPoint, QEvent, Signal
from pyface.qt.QtGui import (
    QApplication, QCursor, QPainter, QWidget, QPen, QStyle
    )
from pyface.util.guisupport import get_app_qt4, start_event_loop_qt4


class PivotSelector(QWidget):
    """ A widget to select the pivot level and rearrange pivot order
    """

    selectorLevelChanged = Signal(int)

    selectorOrderingChanged = Signal(list)

    _dragging_selector = False
    _dragging_name = -1
    _selectors = []
    _selector_height = 4
    _selected = -1

    def __init__(self, parent=None):
        """ Initialize a PivotSelector.

        Parameters
        ----------
        parent : QWidget, optional
            The parent of this selector widget, or None if the header has
            no parent
        """
        super(PivotSelector, self).__init__(parent)
        self.setAttribute(Qt.WA_Hover)

    def selectors(self):
        """ Get the current selectors

        The selectors are returned in the current visual order

        Returns
        -------
        result : list
            The current selector strings

        """
        return self._selectors

    def setSelectors(self, selectors):
        """ Set the current selectors

        Parameters
        ----------
        selectors : list
            The pivot selectors to show. List items must be strings

        """
        self._selectors = selectors
        self._selected = len(selectors) - 1

        # Cache the widths
        style = self.style()
        fm = self.fontMetrics()
        border = (style.pixelMetric(QStyle.PM_DefaultFrameWidth) + 1)* 2
        margin = style.pixelMetric(QStyle.PM_ButtonMargin)
        widths = []
        for sel in self._selectors:
            widths.append(fm.width(sel)+border+margin)
        self._widths = widths

        self.update()

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def paintEvent(self, event):
        """ A reimplemented virtual method.

        """
        painter = QPainter(self)

        # Paint all the selectors side by side
        fm = self.fontMetrics()

        style = self.style()
        border = (style.pixelMetric(QStyle.PM_DefaultFrameWidth) + 1)* 2
        margin = style.pixelMetric(QStyle.PM_ButtonMargin)

        rect = QRect()
        rect.setHeight(fm.height()+border)
        rect.setTopLeft(QPoint(margin/2, self._selector_height))
        for i, sel in enumerate(self._selectors):
            width = fm.width(sel) + border
            rect.setWidth(width)
            if i <= self._selected:
                painter.setPen(Qt.black)
            else:
                painter.setPen(Qt.gray)
            painter.drawText(rect, Qt.AlignCenter, str(sel))
            painter.setPen(Qt.gray)
            painter.drawRect(rect)

            # Now draw the selector
            if i == self._selected:
                painter.setPen(QPen(Qt.gray, 3.0, join=Qt.MiterJoin))
                sh = self._selector_height
                tr = rect.topRight() + QPoint(margin/2 + 1, -sh/2)
                br = rect.bottomRight() + QPoint(margin/2 + 1, sh/2)
                offset = QPoint(6, 0)
                painter.drawPolyline([tr-offset, tr, br, br-offset])

            rect.moveLeft(rect.left()+width+margin)


    def sizeHint(self):
        """ A reimplemented virtual method.

        Returns
        -------
        result : QSize
            The default size for this widget

        """
        style = self.style()
        fm = self.fontMetrics()
        border = (style.pixelMetric(QStyle.PM_DefaultFrameWidth) + 1)* 2
        margin = style.pixelMetric(QStyle.PM_ButtonMargin)
        height = fm.height() + border + self._selector_height
        return QSize(sum(self._widths)+border, height)

    def event(self, event):
        if (event.type() == QEvent.HoverMove and
            not self._dragging_selector and self._dragging_name == -1):
            if self.selectorRect().contains(event.pos()):
                QApplication.setOverrideCursor(QCursor(Qt.SizeHorCursor))
            else:
                QApplication.setOverrideCursor(QCursor(Qt.OpenHandCursor))
        elif (event.type() == QEvent.HoverLeave):
            QApplication.restoreOverrideCursor()
        return super(PivotSelector, self).event(event)

    def mousePressEvent(self, event):
        if self.selectorRect().contains(event.pos()):
            self._dragging_selector = True
        else:
            # Check which box we clicked on
            x, r, l = event.pos().x(), 0, 0
            for i, width in enumerate(self._widths):
                r += width
                if l <= x <= r:
                    self._dragging_name = i
                    QApplication.setOverrideCursor(QCursor(Qt.ClosedHandCursor))
                    break
                l += width
        return super(PivotSelector, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging_selector:
            x, edge = event.pos().x(), 0
            for i, width in enumerate(self._widths):
                edge += width
                if abs(x - edge) < 10:
                    self._selected = i
                    self.update()
                    break
        elif self._dragging_name != -1:
            # Animate dragging
            sel, selectors = self._dragging_name, self._selectors[:]
            x, l = event.pos().x(), 0,
            for i, width in enumerate(self._widths):
                if abs(x - l) < 4:
                    selectors[i], selectors[sel] = selectors[sel], selectors[i]
                    self.setSelectors(selectors)
                    break
                l += width
        return super(PivotSelector, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging_selector:
            self._dragging_selector = False
            self.selectorLevelChanged.emit(self._selected)
        elif self._dragging_name != -1:
            self._dragging_name = -1
            self.selectorOrderingChanged.emit(self._selectors)
            QApplication.restoreOverrideCursor()
        return super(PivotSelector, self).mouseReleaseEvent(event)

    def selectorRect(self):
        # calculate the rect of the selector
        style = self.style()
        fm = self.fontMetrics()
        border = (style.pixelMetric(QStyle.PM_DefaultFrameWidth) + 1)* 2
        margin = style.pixelMetric(QStyle.PM_ButtonMargin)
        height = fm.height() + border + self._selector_height
        return QRect(sum(self._widths[:self._selected+1]), 0, 4, height)

def main():
    app = get_app_qt4()
    ps = PivotSelector()
    ps.setSelectors(["Industry", "Counterparty", "Trader"])
    ps.show()
    start_event_loop_qt4(app)


if __name__ == '__main__':
    main()
