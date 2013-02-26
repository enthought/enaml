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

        # XXX This is a hack
        from chaco.api import RdBu, DataRange1D

        self._cm = cm = RdBu(range=DataRange1D())
        cm.range.low = -0.1
        cm.range.high = 0.1

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

        cell = QColor(152, 186, 210)
        top_border = cell.lighter(110)
        bottom_border = cell.darker(200)
        fm = self.fontMetrics()
        leading = fm.lineSpacing()

        max_depth = self._depth

        for depth in range(max_depth, 0, -1):
            for groups in self._rect_cache[depth]:
                for i, (name, rect, color) in enumerate(groups): #self._rect_cache[depth]):
                    if depth == max_depth:
                        cell = QColor(*(color*255))
                        painter.fillRect(rect, cell)

                        top_border = cell.lighter()
                        bottom_border = cell.darker()
                        painter.setPen(bottom_border)
                        painter.drawPolyline([rect.bottomLeft(), rect.bottomRight(),
                                              rect.topRight()])
                        painter.setPen(top_border)
                        painter.drawPolyline([rect.topRight(), rect.topLeft(),
                                              rect.bottomLeft()])

                    else:
                        painter.setPen(Qt.black)
                        painter.drawRect(rect)

                    if depth in (1, max_depth):
                        rect = rect.adjusted(3,3,0,0)
                        painter.setPen(bottom_border)
                        if i == 0 and not depth == 1:
                            rect.adjust(0,leading,0,0)
                        elif depth == 1:
                            painter.setPen(Qt.black)
                        painter.drawText(rect, Qt.AlignLeft | Qt.AlignTop, str(name))

        painter.setPen(Qt.gray)
        #painter.drawRect(self.rect().adjusted(0,0,-1,-1))

    def _update(self):
        # Recompute layouts
        self.layout()
        self.update()

    def layout(self):
        rect = self.rect().adjusted(1,1,-1,-1)
        aggregate = self._model.engine.aggregates
        self._rect_cache = defaultdict(list)
        self.squarifyLayout(rect, aggregate)

    def squarifyLayout(self, bounds, aggregates, depth=1, index=tuple()):
        column, aggfunc = aggregates[0]
        pt = self._model.engine._get_pivot_table(aggregates[0], depth, 0).sort(column, ascending=False)[column]

        pt2 = self._model.engine._get_pivot_table(aggregates[1], depth, 0)[aggregates[1][0]]

        if isinstance(pt.index, pandas.MultiIndex):
            # XXX WTF the multiindex isn't working properly
            # for a Series
            for i in index:
                pt = pt.ix[i]
                pt2 = pt2.ix[i]

        x, y, w, h = bounds.x(), bounds.y(), bounds.width(), bounds.height()
        rects = self._layout(pt, x, y, w, h)

        self._rect_cache[depth].append(zip(pt.index, rects, self._cm.map_screen(pt2.ix[pt.index])))

        if depth >= self._model.engine.max_depth:
            return

        for idx, rect in zip(pt.index, rects):
            self.squarifyLayout(rect, aggregates, depth+1, index+(idx,))

    def _layout(self, pt, x, y, w, h):
        size = len(pt)

        if size == 0: return []

        if (size < 2):
            return self._slice_layout(pt, x, y, w, h)

        total = pt.sum()

        mid = 0
        a = pt.irow(0) / total
        b = a

        if (w < h):
            while (mid < size):
                aspect = self.normAspect(h, w, a, b)
                q = pt.irow(mid) / total

                if self.normAspect(h,w,a,b+q) > aspect:
                    break

                mid += 1
                b += q

            rects = self._slice_layout(pt[:mid+1], x, y, w, round(h*b))
            return rects + self._layout(pt[mid+1:], x, y+round(h*b),w,round(h*(1-b)))
        else:
            while (mid < size):
                aspect = self.normAspect(w,h,a,b)
                q = pt.irow(mid) / total

                if self.normAspect(w,h,a,b+q) > aspect:
                    break

                mid += 1
                b += q

            rects = self._slice_layout(pt[:mid+1], x, y, round(w*b), h)
            return rects + self._layout(pt[mid+1:], x+round(w*b), y, round(w*(1-b)),h)

    def normAspect(self, big, small, a, b):
        x = (big * b) / (small * a / b)
        if x < 1: return 1/x
        else: return x

    def _slice_layout(self, pt, x, y, width, height):
        factors = pt / pt.sum()
        accum = pandas.np.zeros(len(factors))
        accum[1:] = factors[:-1].cumsum()

        if width <= height:
            rects = [QRect(x, y+round(height*(1-a-f)), width, round(height*f)) for f, a in zip(factors, accum)]
        else:
            rects = [QRect(x + round(width*(1-a-f)), y, round(width*f), height) for f, a in zip(factors, accum)]

        return rects


def treemap_view(engine, model_class=PivotModel, view_class=TreemapView,
                 parent = None):
    """ Return a TreemapView configured to display a pandas engine
    """

    model = model_class(engine)

    view = view_class(parent)

    view.setModel(model)
    return view

