import pandas
from collections import defaultdict
from enaml.qt.qt.QtCore import Qt, QRect
from enaml.qt.qt.QtGui import (
    QWidget, QPainter, QColor, QSizePolicy
    )

from ..tabular_model import NullModel
from .pivot_ui import PivotModel
from .pandas_pivot import AggregationNode, MarginNode


class TreemapView(QWidget):
    def __init__(self, parent):
        super(TreemapView, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._rect_cache = defaultdict(list)
        self._depth = 0
        self._model = NullModel()
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def model(self):
        """ Get the model being viewed by the widget

        Returns
        -------
        result : TabularModel
            The tabular model being viewed by the widget

        """
        return self._model

    def setModel(self, model):
        """ Set the model being viewed by the widget

        Parameters
        ----------
        model : TabularModel
            The model to be viewed by the widget

        """
        assert isinstance(model, PivotModel)
        if self._model:
            self._model.dataChanged.disconnect(self._update)
        self._model = model
        self._depth = model.engine.max_depth
        self._update()
        self._model.dataChanged.connect(self._update)

    def setDepth(self, depth):
        self._depth = depth
        self.update()

    def resizeEvent(self, event):
        self._update()
        super(TreemapView, self).resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)

        cell = QColor(137, 207, 230)
        top_border = cell.lighter()
        bottom_border = cell.darker()

        max_depth = self._depth

        for index, rect in iter(self._rect_cache[max_depth]):
            painter.fillRect(rect, cell)

            top_border = cell.lighter()
            bottom_border = cell.darker()
            painter.setPen(bottom_border)
            painter.drawPolyline([rect.bottomLeft(), rect.bottomRight(),
                                  rect.topRight()])
            painter.setPen(top_border)
            painter.drawPolyline([rect.topRight(), rect.topLeft(),
                                  rect.bottomLeft()])

            painter.setPen(bottom_border)
            painter.drawText(rect.adjusted(3,3,0,0), Qt.AlignLeft | Qt.AlignTop, index)

        painter.setPen(Qt.gray)
        painter.drawRect(self.rect().adjusted(0,0,-1,-1))

    def _update(self):
        # Recompute layouts
        self.layout()
        self.update()

    def layout(self):
        rect = self.rect().adjusted(1,1,-1,-1)
        aggregate = self._model.engine.aggregates[0]
        self._rect_cache = defaultdict(list)
        self.squarifyLayout(rect, aggregate)

    def squarifyLayout(self, bounds, aggregate, depth=1, index=tuple()):
        column, aggfunc = aggregate
        pt = self._model.engine._get_pivot_table(aggregate, depth, 0).sort(column, ascending=False)[column]

        if isinstance(pt.index, pandas.MultiIndex):
            # XXX WTF the multiindex isn't working properly
            # for a Series
            for i in index:
                pt = pt.ix[i]

        rects = self._layout(pt, 0, len(pt) - 1, bounds)

        self._rect_cache[depth].extend(zip(pt.index, rects))

        if depth >= self._model.engine.max_depth:
            return

        for idx, rect in zip(pt.index, rects):
            self.squarifyLayout(rect, aggregate, depth+1, index+(idx,))

    def _layout(self, pt, start, end, bounds):
        if start > end: return []

        if (end - start < 2):
            return self._slice_layout(pt, start, end, bounds)

        x, y, w, h = bounds.x(), bounds.y(), bounds.width(), bounds.height()

        total = pt[start:end+1].sum()

        mid = start
        a = pt[start] / total
        b = a

        if (w < h):
            while (mid <= end):
                aspect = self.normAspect(h, w, a, b)
                q = pt[mid] / total

                if self.normAspect(h,w,a,b+q) > aspect:
                    break

                mid += 1
                b += q

            rects = self._slice_layout(pt, start, mid, QRect(x, y, w, round(h*b)))
            return rects + self._layout(pt, mid+1, end, QRect(x, y+round(h*b),w,round(h*(1-b))))
        else:
            while (mid <= end):
                aspect = self.normAspect(w,h,a,b)
                q = pt[mid] / total

                if self.normAspect(w,h,a,b+q) > aspect:
                    break

                mid += 1
                b += q

            rects = self._slice_layout(pt, start, mid, QRect(x,y, round(w*b), h))
            return rects + self._layout(pt, mid+1, end, QRect(x+round(w*b), y, round(w*(1-b)),h))

    def normAspect(self, big, small, a, b):
        x = (big * b) / (small * a / b)
        if x < 1: return 1/x
        else: return x

    def _slice_layout(self, pt, start, end, bounds):
        total = accumulator = 0

        total = pt[start:end+1].sum()

        is_horiz = (bounds.width() > bounds.height())

        rects = []
        for i in range(start, end+1):
            factor = pt[i] / total
            rect = QRect()
            if not is_horiz:
                rect.setX(bounds.x())
                rect.setWidth(bounds.width())
                rect.setY(bounds.y()+round(bounds.height()*(1-accumulator-factor)))
                rect.setHeight(round(bounds.height()*factor))
            else:
                rect.setX(bounds.x()+round(bounds.width()*(1-accumulator-factor)))
                rect.setWidth(round(bounds.width()*factor))
                rect.setY(bounds.y())
                rect.setHeight(bounds.height())
            rects.append(rect)
            accumulator += factor
        return rects


def treemap_view(engine, model_class=PivotModel, view_class=TreemapView,
                 parent = None):
    """ Return a TreemapView configured to display a pandas engine
    """

    model = model_class(engine)

    view = view_class(parent)

    view.setModel(model)
    return view

