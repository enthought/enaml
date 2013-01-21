#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

from enaml.qt.qt.QtCore import Qt, QRect, QLine
from enaml.qt.qt.QtGui import (
    QPainter, QAbstractScrollArea, QTextOption, QColor,
    QWidget
    )

from .q_fixed_size_header import QFixedSizeHeader
from .qt_tabular_style import QtTabularStyle
from .tabular_model import TabularModel, NullModel
from .q_tabular_header import QTabularHeader


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
        self._v_lines_visible = True
        self._h_lines_visible = True
        viewport = self.viewport()
        viewport.setAttribute(Qt.WA_StaticContents, True)
        viewport.setAutoFillBackground(True)
        viewport.setFocusPolicy(Qt.ClickFocus)
        self._updateViewportMargins()
        self._updateGeometries()
        self.setMouseTracking(True)
        # Attribute that controls whether drawing
        # damaged regions is enabled. If this is
        # true paintUpdatedRegion will be called
        # with each damaged rect in tabular view
        # after the paint of that damaged rect
        # is over.ie QTabularView gets a first
        # shot at painting into the damaged rect
        # then paintUpdatedRegion gets an opportunity
        # to draw over that.
        self._debug_draw_regions = False
        self._debug_color_generator = None

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

    def rowHeader(self):
        """ Get the row header in use by the widget.

        Returns
        -------
        result : QTabularHeader
            The tabular row header for the widget.

        """
        return self._v_header

    def setRowHeader(self, header):
        """ Set the row header in use by the widget.

        Parameters
        ----------
        v_header : QTabularHeader
            The tabular row header for the widget.

        """
        assert isinstance(header, QTabularHeader)
        header.setParent(self)
        self._v_header = header
        self._v_header.setModel(self._model)
        self._updateGeometries()

    def columnHeader(self):
        """ Get the column header in use by the widget.

        Returns
        -------
        result : QTabularHeader
            The tabular column header for the widget.

        """
        return self._h_header

    def setColumnHeader(self, header):
        """ Set the column header in use by the widget.

        Parameters
        -------
        result : QTabularHeader
            The tabular column header for the widget.

        """
        assert isinstance(header, QTabularHeader)
        header.setParent(self)
        self._h_header = header
        self._h_header.setModel(self._model)
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

    def horizontalLinesVisible(self):
        """ Get whether or not horizontal grid lines are visible.

        Returns
        -------
        result : bool
            True if horizontal lines are visible, False otherwise.

        """
        return self._h_lines_visible

    def setHorizontalLinesVisible(self, visible):
        """ Set whether or not horizontal grid lines are visible.

        Parameters
        ----------
        visible : bool
            True if horizontal lines should be show, False otherwise.

        """
        self._h_lines_visible = visible
        self.update()

    def verticalLinesVisible(self):
        """ Get whether or not vertical grid lines are visible.

        Returns
        -------
        result : bool
            True if vertical lines are visible, False otherwise.

        """
        return self._v_lines_visible

    def setVerticalLinesVisible(self, visible):
        """ Set whether or not vertical grid lines are visible.

        Parameters
        ----------
        visible : bool
            True if vertical lines should be show, False otherwise.

        """
        self._v_lines_visible = visible
        self.update()

    def setDebugDrawRegions(self, value):
        """ Set whether to highlight regions being painted in paintEvent

        Parameters
        ----------
        value : bool
            Set whether or not to highlight regions being updated

        """
        self._debug_draw_regions = value

    def paintUpdatedRegion(self, painter, rect):
        """ Draw debug visualization to highlight damaged regions

        This is meant for development / debugging use only and is
        useful to keep track of the position and extent of regions
        being invalidated and redrawn. This function is only invoked
        if self._debug_draw_regions is True.

        Parameters
        ----------

        painter : QPainter
            Active painter which is active on current widget

        rect : QRect
            Rectangle which is damaged

        """
        if self._debug_color_generator is None:
            self._debug_color_generator = self._buildDebugColorGenerator()
        color = self._debug_color_generator.next()
        painter.fillRect(rect, color)

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

        # Set the horizontal header geometry. Only set the full geometry
        # when the position has a descrepancy, otherwise the damaged
        # region will not be computed correctly.
        if h_header.x() != geo.x():
            h_header.setGeometry(geo.x(), 0, geo.width(), geo.y())
        else:
            h_header.resize(geo.width(), geo.y())

        # Set the vertical header geometry. Only set the full geometry
        # when the position has a descrepancy, otherwise the damaged
        # region will not be computed correctly.
        if v_header.y() != geo.y():
            v_header.setGeometry(0, geo.y(), geo.x(), geo.height())
        else:
            v_header.resize(geo.x(), geo.height())

    def _buildDebugColorGenerator(self):
        alpha = 125
        level = 200
        colors = [
                    QColor(level, 0, 0, alpha),
                    QColor(0, level, 0, alpha),
                    QColor(0, 0, level, alpha)
                ]
        idx = 0
        color_len = len(colors)
        while 1:
            yield colors[idx % color_len]
            idx += 1

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
        if self._h_header.count() == 0 or self._v_header.count() == 0:
            return
        painter = QPainter(self.viewport())
        try:
            self.paint(painter, event)
        except Exception:
            painter.end()
            raise

    def paint(self, painter, event):

        # Pre-fetch commons data as locals
        model = self._model
        h_header = self._h_header
        v_header = self._v_header
        h_offset = h_header.offset()
        v_offset = v_header.offset()

        # The cell rect is updated during iteration. Only a single rect
        # object is allocated for the entire paint event.
        cell_rect = QRect()

        # The grid line is updated during iteration. Only a single line
        # object is allocated for the entire paint event.
        grid_line = QLine()

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

            # Compute the logical indices and sizes for the region.
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

            # Fetch the data and the styles for the logical indices.
            num_rows = len(row_indices)
            num_cols = len(col_indices)
            num_cells = num_rows * num_cols
            indexable = (list, tuple)

            row_styles = model.row_styles(row_indices)
            if row_styles is None:
                row_styles = [None] * num_rows
            elif not isinstance(row_styles, indexable):
                row_styles = list(row_styles)
            assert len(row_styles) == num_rows

            column_styles = model.column_styles(col_indices)
            if column_styles is None:
                column_styles = [None] * num_cols
            elif not isinstance(column_styles, indexable):
                column_styles = list(column_styles)
            assert len(column_styles) == num_cols

            cell_data = model.data(row_indices, col_indices)
            if cell_data is None:
                cell_data = [None] * num_cells
            elif not isinstance(cell_data, indexable):
                cell_data = list(cell_data)
            assert len(cell_data) == num_cells

            cell_styles = model.cell_styles(row_indices, col_indices, cell_data)
            if cell_styles is None:
                cell_styles = [None] * num_cells
            elif not isinstance(cell_styles, indexable):
                cell_styles = list(cell_styles)
            assert len(cell_styles) == num_cells

            # Compute the painting bounds
            start_x = h_header.sectionPosition(first_visual_col) - h_offset
            start_y = v_header.sectionPosition(first_visual_row) - v_offset
            max_x = start_x + sum(col_widths) - 1
            max_y = start_y + sum(row_heights) - 1

            # Paint grid lines first since a cell border may paint over.
            painter.save()
            painter.setPen(Qt.gray)
            if self._v_lines_visible:
                x_run = start_x
                for col_width in col_widths:
                    x_run += col_width
                    grid_line.setLine(x_run - 1, y1, x_run - 1, max_y)
                    painter.drawLine(grid_line)
            if self._h_lines_visible:
                y_run = start_y
                for row_height in row_heights:
                    y_run += row_height
                    grid_line.setLine(x1, y_run - 1, max_x, y_run - 1)
                    painter.drawLine(grid_line)
            painter.restore()

            # Prefetch frequently called bound methods as locals.
            setRect = cell_rect.setRect
            paintCell = self.paintCell
            save = painter.save
            restore = painter.restore

            # Paint the dirty cells. The space available for drawing the
            # cell includes the grid line on all sides. Grid lines are
            # shared space between adjacent cells
            row_idx = 0
            col_idx = 0
            cell_idx = 0
            y_run = start_y
            for row_height in row_heights:
                x_run = start_x
                row_style = row_styles[row_idx]
                for col_width in col_widths:
                    setRect(x_run - 1, y_run - 1, col_width + 1, row_height + 1)
                    save()
                    paintCell(
                        painter, cell_rect, cell_data[cell_idx],
                        cell_styles[cell_idx], column_styles[col_idx],
                        row_style,
                    )
                    restore()
                    x_run += col_width
                    cell_idx += 1
                    col_idx += 1
                row_idx += 1
                col_idx = 0
                y_run += row_height

            if self._debug_draw_regions:
                self.paintUpdatedRegion(painter, rect)

    def paintCell(self, painter, rect, data, cell_style, col_style, row_style):
        # If there is no style, short circuit the complex painting.
        if cell_style is None and col_style is None and row_style is None:
           if data is not None:
               painter.drawText(rect, Qt.AlignCenter, str(data))
           return

        q_cell_style = None
        if cell_style is not None:
            if '__q_style' in cell_style:
                q_cell_style = cell_style['__q_style']
            else:
                q_cell_style = QtTabularStyle.init_from(cell_style)
                cell_style['__q_style'] = q_cell_style

        q_col_style = None
        if col_style is not None:
            if '__q_style' in col_style:
                q_col_style = col_style['__q_style']
            else:
                q_col_style = QtTabularStyle.init_from(col_style)
                col_style['__q_style'] = q_col_style

        q_row_style = None
        if row_style is not None:
            if '__q_style' in row_style:
                q_row_style = row_style['__q_style']
            else:
                q_row_style = QtTabularStyle.init_from(row_style)
                row_style['__q_style'] = q_row_style

        # Extract the style according to precedence.
        cell_background = None
        col_background = None
        row_background = None
        foreground = None
        padding = None
        margin = None
        border = None
        align = None
        font = None
        if q_cell_style is not None:
            cell_background = q_cell_style.background
            foreground = q_cell_style.foreground
            padding = q_cell_style.padding
            margin = q_cell_style.margin
            border = q_cell_style.border
            align = q_cell_style.align
            font = q_cell_style.font
        if q_col_style is not None:
            col_background = q_col_style.background
            foreground = foreground or q_col_style.foreground
            padding = padding or q_col_style.padding
            margin = margin or q_col_style.margin
            border = border or q_col_style.border
            align = align or q_col_style.align
            font = font or q_col_style.font
        if q_row_style is not None:
            row_background = q_row_style.background
            foreground = foreground or q_row_style.foreground
            padding = padding or q_row_style.padding
            margin = margin or q_row_style.margin
            border = border or q_row_style.border
            align = align or q_row_style.align
            font = font or q_row_style.font

        # Adjust for margins.
        if margin is not None:
            rect.adjust(*margin)
        else:
            # XXX make default margin configurable
            rect.adjust(1, 1, -1, -1)

        # Fill the background.
        if row_background is not None:
            painter.fillRect(rect, row_background)
        if col_background is not None:
            painter.fillRect(rect, col_background)
        if cell_background is not None:
            painter.fillRect(rect, cell_background)

        # Draw the borders
        if border is not None:
            pen = None
            offset = 0
            extra = 0
            x1 = rect.x()
            y1 = rect.y()
            x2 = rect.right() + 1
            y2 = rect.bottom() + 1
            if border.top is not None:
                pen = border.top
                offset, r = divmod(max(1, pen.width()), 2)
                extra = offset + r
                painter.setPen(pen)
                painter.drawLine(
                    x1 + offset, y1 + offset, x2 - extra, y1 + offset
                )
                rect.adjust(0, offset*2, 0, 0)
            if border.bottom is not None:
                if border.bottom is not pen:
                    pen = border.bottom
                    offset, r = divmod(max(1, pen.width()), 2)
                    extra = offset + r
                    painter.setPen(pen)
                painter.drawLine(
                    x1 + offset, y2 - extra, x2 - extra, y2 - extra
                )
                rect.adjust(0, 0, 0, -offset*2)
            if border.left is not None:
                if border.left is not pen:
                    pen = border.left
                    offset, r = divmod(max(1, pen.width()), 2)
                    extra = offset + r
                    painter.setPen(pen)
                painter.drawLine(
                    x1 + offset, y1 + offset, x1 + offset, y2 - extra
                )
                rect.adjust(offset*2, 0, 0, 0)
            if border.right is not None:
                if border.right is not pen:
                    pen = border.right
                    offset, r = divmod(max(1, pen.width()), 2)
                    extra = offset + r
                    painter.setPen(pen)
                painter.drawLine(
                    x2 - extra, y1 + offset, x2 - extra, y2 - extra
                )
                rect.adjust(0, 0, -offset*2, 0)

        # Adjust for padding.
        if padding is not None:
            rect.adjust(*padding)

        # Draw the content.
        if data is not None:
            if align is None:
                align = Qt.AlignCenter
            if font is not None:
                painter.setFont(font)
            if foreground is not None:
                painter.setPen(foreground)
            # XXX support data formatters.
            painter.drawText(rect, align, unicode(data))

