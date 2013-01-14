#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

from enaml.qt.qt.QtCore import Qt, QRect, QLine
from enaml.qt.qt.QtGui import QPainter, QAbstractScrollArea

from .q_fixed_size_header import QFixedSizeHeader
from .tabular_model import TabularModel, NullModel


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
    """ A widget which renders a scrolling 2D over a TabularModel.

    This widget is fully lazy and only requests data for the portion of
    the model which is visible in the viewport. The limits of the view
    are quite large: when scrolling by pixel, it has a virtual canvas
    size of ~2.1 billion pixels in either direction; when scrolling by
    item, the capacity is ~2.1 billion items in either direction.

    """
    #: Scroll the widget in the specified direction by pixel.
    ScrollPerPixel = 0

    #: Scroll the widget in the specified direction by item.
    ScrollPerItem = 1

    def __init__(self, parent=None):
        """ Initialize a QTabularView.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget of this widget, or None if the widget has
            no parent.

        """
        super(QTabularView, self).__init__(parent)
        self._model = NullModel()
        self._v_header = QFixedSizeHeader(Qt.Vertical, self)
        self._h_header = QFixedSizeHeader(Qt.Horizontal, self)
        self._h_scroll_policy = QTabularView.ScrollPerPixel
        self._v_scroll_policy = QTabularView.ScrollPerPixel
        viewport = self.viewport()
        viewport.setAttribute(Qt.WA_StaticContents, True)
        viewport.setAutoFillBackground(True)
        viewport.setFocusPolicy(Qt.ClickFocus)
        self._updateViewportMargins()
        self._updateGeometries()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def model(self):
        """ Get the model being viewed by the widget.

        Returns
        -------
        result : TabularModel
            The tabular model being viewed by the widget.

        """
        return self._model

    def setModel(self, model):
        """ Set the model being viewed by the widget.

        Parameters
        ----------
        model : TabularModel
            The model to be viewed by the widget.

        """
        assert isinstance(model, TabularModel)
        self._model = model
        self._v_header.setModel(model)
        self._h_header.setModel(model)
        self._updateGeometries()

    def horizontalScrollPolicy(self):
        """ Get the horizontal scroll policy for the widget.

        Returns
        -------
        result : int
            The horizontal scroll policy of the widget. This will be
            one of enum values `QTabularView.ScrollPerPixel` or
            `QTabularView.ScrollPerItem`.

        """
        return self._h_scroll_policy

    def setHorizontalScrollPolicy(self, policy):
        """ Set the horizontal scroll policy for the widget.

        Parameters
        ----------
        policy : int
            The horizontal scroll policy for the widget. This must
            be one of enum values `QTabularView.ScrollPerPixel` or
            `QTabularView.ScrollPerItem`.

        """
        valid = (QTabularView.ScrollPerPixel, QTabularView.ScrollPerItem)
        assert policy in valid
        self._h_scroll_policy = policy
        self._updateGeometries()

    def verticalScrollPolicy(self):
        """ Get the vertical scroll policy for the widget.

        Returns
        -------
        result : int
            The vertical scroll policy of the widget. This will be
            one of enum values `QTabularView.ScrollPerPixel` or
            `QTabularView.ScrollPerItem`.

        """
        return self._v_scroll_policy

    def setVerticalScrollPolicy(self, policy):
        """ Set the vertical scroll policy for the widget.

        Parameters
        ----------
        policy : int
            The vertical scroll policy for the widget. This must be
            one of enum values `QTabularView.ScrollPerPixel` or
            `QTabularView.ScrollPerItem`.

        """
        valid = (QTabularView.ScrollPerPixel, QTabularView.ScrollPerItem)
        assert policy in valid
        self._v_scroll_policy = policy
        self._updateGeometries()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _updateViewportMargins(self):
        """ Update the margins for the viewport.

        This method should be called when either header's header size
        or visibility changes. The viewport margins will be updated to
        allow for enough space for each header.

        """
        v_header = self._v_header
        h_header = self._h_header
        left = top = 0
        # The -1 accounts for the fact that QAbstractScrollArea will
        # yield a viewport position of (1, 1) with margins of zero.
        if h_header.isVisibleTo(self):
            top = h_header.headerSize() - 1
        if v_header.isVisibleTo(self):
            left = v_header.headerSize() - 1
        self.setViewportMargins(left, top, 0, 0)

    def _updateGeometries(self):
        """ Update the current range of the scroll bars.

        This method can be called as-needed to update the range of the
        scroll bars for the size of the viewport. The current scroll
        policies are taken into account when performing the update.

        """
        # When scrolling per pixel, the scrollbar range is the length
        # of the header minus the size of the viewport. When scrolling
        # by item, the range is the number of items minus the number
        # of trailing items which can fit on the screen.
        h_header = self._h_header
        v_header = self._v_header
        h_bar = self.horizontalScrollBar()
        v_bar = self.verticalScrollBar()
        geo = self.viewport().geometry()

        # Set the horizontal scrollbar range.
        if self._h_scroll_policy == QTabularView.ScrollPerPixel:
            h_bar.setRange(0, h_header.length() - geo.width())
        else:
            delta = h_header.trailingSpan(geo.width())
            h_max = max(0, h_header.count() - delta)
            h_bar.setRange(0, h_max)

        # Set the vertical scrollbar range.
        if self._v_scroll_policy == QTabularView.ScrollPerPixel:
            v_bar.setRange(0, v_header.length() - geo.height())
        else:
            delta = v_header.trailingSpan(geo.height())
            v_max = max(0, v_header.count() - delta)
            v_bar.setRange(0, v_max)

        # Set the horizontal header geometry.
        if h_header.x() != geo.x():
            h_header.setGeometry(geo.x(), 0, geo.width(), geo.y())
        else:
            h_header.resize(geo.width(), geo.y())

        # Set the vertical header geometry.
        if v_header.y() != geo.y():
            v_header.setGeometry(0, geo.y(), geo.x(), geo.height())
        else:
            v_header.resize(geo.x(), geo.height())

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def resizeEvent(self, event):
        """ A reimplemented virtual method.

        This resize event handler ensures the scroll bar ranges are
        updated when the size of the viewport changes.

        """
        super(QTabularView, self).resizeEvent(event)
        self._updateGeometries()

    def scrollContentsBy(self, dx, dy):
        """ A reimplemented virtual method.

        This scroll handler updates the offsets of the headers and then
        scrolls the viewport appropriately. The current scroll policies
        are taken into account when computing the offsets.

        """
        # Update the horizontal header offset.
        if dx != 0:
            header = self._h_header
            old = header.offset()
            new = self.horizontalScrollBar().value()
            if self._h_scroll_policy == QTabularView.ScrollPerItem:
                new = header.sectionPosition(new)
            header.setOffset(new)
            dx = old - new

        # Update the vertical header offset.
        if dy != 0:
            header = self._v_header
            old = header.offset()
            new = self.verticalScrollBar().value()
            if self._v_scroll_policy == QTabularView.ScrollPerItem:
                new = header.sectionPosition(new)
            header.setOffset(new)
            dy = old - new

        # Scroll the widget by the computed deltas.
        if dx != 0 or dy != 0:
            viewport = self.viewport()
            size = viewport.size()
            if abs(dx) >= size.width() or abs(dy) >= size.height():
                viewport.update()
            else:
                scrollWidget(viewport, dx, dy)

    def paintEvent(self, event):
        """ A reimplemented virtual method.

        This paint event handler repaints the grid only for the damaged
        region of the viewport.

        """
        # If there are no rows or columns, nothing needs to be drawn.
        h_header = self._h_header
        v_header = self._v_header
        if h_header.count() == 0 or v_header.count() == 0:
            return

        painter = QPainter(self.viewport())

        # The cell rect is updated during iteration. Only a single rect
        # object is allocated for the entire paint event.
        cell_rect = QRect()

        # The grid line is updated during iteration. Only a single line
        # object is allocated for the entire paint event.
        grid_line = QLine()

        # Prefetch common attributes as locals.
        model = self._model
        h_offset = h_header.offset()
        v_offset = v_header.offset()

        for rect in event.region().rects():

            # Set the clip rect to avoid overdrawing onto other parts
            # of the region. This is crucial to elimination overdrawing
            # of antialiased fonts when scrolling one pixel at a time.
            painter.setClipRect(rect)

            # Compute the index bounds of the dirty rect.
            x1 = rect.x()
            x2 = x1 + rect.width()
            y1 = rect.y()
            y2 = y1 + rect.height()
            first_visual_row = v_header.visualIndexAt(y1 + v_offset)
            last_visual_row = v_header.visualIndexAt(y2 + v_offset)
            first_visual_col = h_header.visualIndexAt(x1 + h_offset)
            last_visual_col = h_header.visualIndexAt(x2 + h_offset)

            # If an index is out of bounds, there is nothing to draw.
            if first_visual_row == -1 or first_visual_col == -1:
                continue

            # Clip the trailing indices to the valid bounds.
            if last_visual_row == -1:
                last_visual_row = v_header.count() - 1
            if last_visual_col == -1:
                last_visual_col = h_header.count() - 1

            # Compute the logical indices, data, and paint start.
            col_widths = []
            col_indices = []
            for idx in xrange(first_visual_col, last_visual_col + 1):
                col_widths.append(h_header.sectionSize(idx))
                col_indices.append(h_header.logicalIndex(idx))
            row_heights = []
            row_indices = []
            for idx in xrange(first_visual_row, last_visual_row + 1):
                row_heights.append(v_header.sectionSize(idx))
                row_indices.append(v_header.logicalIndex(idx))
            data = iter(model.data(row_indices, col_indices))
            start_x = h_header.sectionPosition(first_visual_col) - h_offset
            start_y = v_header.sectionPosition(first_visual_row) - v_offset

            # Compute the paint bounds
            max_x = start_x + sum(col_widths) - 1
            max_y = start_y + sum(row_heights) - 1

            # Draw the grid lines first since a cell border may overdraw
            # Each line is drawn on the last pixel of the row or column.
            painter.save()
            painter.setPen(Qt.gray)
            x_run = start_x
            for col_width in col_widths:
                x_run += col_width
                grid_line.setLine(x_run - 1, y1, x_run - 1, max_y)
                painter.drawLine(grid_line)
            y_run = start_y
            for row_height in row_heights:
                y_run += row_height
                grid_line.setLine(x1, y_run - 1, max_x, y_run - 1)
                painter.drawLine(grid_line)
            painter.restore()

            # Draw the cell data for the invalid region.
            try:
                ndata = data.next
                setRect = cell_rect.setRect
                drawText = painter.drawText
                str_ = str
                AlignCenter = Qt.AlignCenter
                y_run = start_y
                for row_height in row_heights:
                    x_run = start_x
                    for col_width in col_widths:
                        setRect(x_run, y_run, col_width, row_height)
                        drawText(cell_rect, AlignCenter, str_(ndata()))
                        x_run += col_width
                    y_run += row_height
            except StopIteration: # ran out of data early
                pass

