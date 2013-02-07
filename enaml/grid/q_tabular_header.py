#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

from enaml.qt.qt.QtCore import Qt, QRect, QPointF, QLine
from enaml.qt.qt.QtGui import QWidget, QPainter, QLinearGradient, QColor

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


class QTabularHeader(QWidget):
    """ A base class for creating headers for use by a QTabularView.

    This class must be subclassed in order to be useful. The subclass
    must implement the abstract api defined below. Default rendering
    is provided and will draw the headers in a single row. If more
    complex rendering is required, subclasses should reimplement the
    paint event.

    The abstract methods defined below will be called *often* by the
    QTabularView. Subclasses should make a concerted effort to ensure
    the implementations are as efficient as possible.

    All visual indices reported by a header must be contiguous. That
    is, if visual indices 0 and 5 exist, then 1, 2, 3, and 4 must also
    exist and in that order. It is the responsibility of the header to
    maintain any relevant internal state for hidden and moved sections.
    The QTabularView always treats a header as a continuous monontonic
    block of visible sections.

    The QTabularView will use the trailing pixel of each section as
    the space to draw the grid line.

    """
    def __init__(self, orientation, parent=None):
        """ Initialize a QTabularHeader.

        Parameters
        ----------
        orientation : Qt.Orientation
            The orientation of the header. This must be either
            Qt.Horizontal or Qt.Vertical.

        parent : QWidget, optional
            The parent of this header, or None of the header has
            no parent.

        """
        super(QTabularHeader, self).__init__(parent)
        assert orientation in (Qt.Horizontal, Qt.Vertical)
        self._orientation = orientation
        self._model = NullModel()
        self._offset = 0
        self._elide_mode = Qt.ElideNone

        # The default header background gradient. XXX make configurable.
        grad = QLinearGradient(QPointF(0, 0), QPointF(0, 1))
        grad.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        grad.setColorAt(0, QColor(255, 255, 255))
        grad.setColorAt(0.75, QColor(230, 230, 230))
        grad.setColorAt(1, QColor(250, 250, 250))
        self._gradient = grad

        # Set the static contents and autofill background flag so that
        # only the damaged regions are included in the paint event. The
        # opaque paint flag could be set instead of autofill background,
        # but that would require detecting invalid regions beyond the
        # extents of the header and filling them with the background
        # color. When painting from Python, that would likely require
        # more time than letting Qt fill the invalid background instead.
        self.setAttribute(Qt.WA_StaticContents, True)
        self.setAutoFillBackground(True)

    def orientation(self):
        """ Get the orientation of the header.

        Returns
        -------
        result : Qt.Orientation
            The orientation of the header. This must be either
            Qt.Horizontal or Qt.Vertical.

        """
        return self._orientation

    def model(self):
        """ Get the model associated with the header.

        Returns
        -------
        result : TabularModel
            The model associated with the header.

        """
        return self._model

    def setModel(self, model):
        """ Set the model associated with the header.

        This method may be overridden by subclasses for more control.

        Parameters
        ----------
        model : TabularModel
            The tabular model to use with the header.

        """
        assert isinstance(model, TabularModel)
        self._model = model

    def offset(self):
        """ Get the current offset of the header.

        The offset of the header is the offset into the virtual length
        for the current zero position of the viewport.

        Returns
        -------
        result : int
            The current offset of the header. This will always be
            greater than or equal to zero.

        """
        return self._offset

    def setOffset(self, offset):
        """ Set the current offset of the header.

        This method updates the offset and then performs a low-level
        scroll so that only the damaged region is updated. Subclasses
        which require more control may reimplement this method.

        Parameters
        ----------
        offset : int
            The desired offset of the header. This must be bounded by
            zero and the header length.

        """
        old = self._offset
        self._offset = offset
        delta = old - offset
        if delta != 0:
            if self.orientation() == Qt.Horizontal:
                if abs(delta) < self.width():
                    scrollWidget(self, delta, 0)
                else:
                    self.update()
            else:
                if abs(delta) < self.height():
                    scrollWidget(self, 0, delta)
                else:
                    self.update()

    def logicalIndexAt(self, position):
        """ Get the logical index which overlaps the position.

        Parameters
        ----------
        position : int
            The visual pixel position to map to a logical index. This
            must always be bounded by zero and the header length.

        Returns
        -------
        result : int
            The logical index for the visual position. On success, this
            will be greater than or equal to zero. On failure, -1 is
            returned indicating the position is out of bounds.

        """
        index = self.visualIndexAt(position)
        if index == -1:
            return index
        return self.logicalIndex(index)

    def setTextElideMode(self, elide_mode):
        """ Set the text elidation mode of the header

        This method updates the offset and then performs a low-level
        scroll so that only the damaged region is updated. Subclasses
        which require more control may reimplement this method.

        Parameters
        ----------
        elide_mode : Qt.TextElideMode
            This property holds the position of the '...' in elided header
            text. It is one of Qt.ElideLeft, Qt.ElideRight, Qt.ElideMiddle, or
            Qt.ElideNone

        """
        self._elide_mode = elide_mode
        self.update()

    def textElideMode(self):
        """ Get the text elide mode of the header

        Returns
        -------
        result : Qt.TextElideMode
            This property holds the position of the '...' in elided header
            text. It is one of Qt.ElideLeft, Qt.ElideRight, Qt.ElideMiddle, or
            Qt.ElideNone

        """
        return self._elide_mode

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    def count(self):
        """ Get the number of visible sections in the header.

        The visible sections are the sections of the header which can
        be viewed by scrolling to the extents of the grid. This count
        should not include sections which have been explicitly hidden
        by the user.

        Returns
        -------
        result : int
            The number of visible sections in the header.

        """
        raise NotImplementedError

    def length(self):
        """ Get the total visible length of the header.

        This is the length of all visible sections in the header. The
        length should not include sections which have been explicitly
        hidden by the user.

        Returns
        -------
        result : int
            The total visible length of the header.

        """
        raise NotImplementedError

    def headerSize(self):
        """ Get the display size for the header.

        Returns
        -------
        result : int
            The size to use by QTabularView when displaying the header.
            For horizontal headers, this will be the header height. For
            vertical headers, this will be the header width.

        """
        raise NotImplementedError

    def sectionSize(self, visual_index):
        """ Get the size for a given visual section.

        Parameters
        ----------
        visual_index : int
            The visual index of the section. This must be bounded by
            zero and the header count.

        Returns
        -------
        result : int
            The size of the given section.

        """
        raise NotImplementedError

    def sectionPosition(self, visual_index):
        """ Get the pixel position for a given visual index.

        Parameters
        ----------
        visual_index : int
            The visual index of the section. This must be bounded by
            zero and the header count.

        Returns
        -------
        result : int
            The position of the given section. It will not be adjusted
            for the header offset.

        """
        raise NotImplementedError

    def trailingSpan(self, length):
        """ Get the number of trailing items covered by a given length.

        This value is used by QTabularView when scrolling per item
        in order to set the ending scroll position.

        Parameters
        ----------
        length : int
            The length of the given coverage request.

        Returns
        -------
        result : int
            The number of items at the end of the end of the header
            covered by the given length.

        """
        raise NotImplementedError

    def visualIndexAt(self, position):
        """ Get the visual index which overlaps the position.

        Parameters
        ----------
        position : int
            The visual pixel position to map to a visual index. This
            must be bounded by zero and the header length.

        Returns
        -------
        result : int
            The visual index for the visual position. On success, this
            will be greater than or equal to zero. On failure, -1 is
            returned indicating the position is out of bounds.

        """
        raise NotImplementedError

    def visualIndex(self, logical_index):
        """ Get the visual index for a given logical index.

        Parameters
        ----------
        logical_index : int
            The logical model index to map to a header visual index.
            This must be bounded by zero and the relevant model row
            or column count.

        Returns
        -------
        result : int
            The visual index for the model index. On success, this will
            be greater than or equal to zero. On failure, -1 is returned
            indicating that logical index has no visual index; i.e that
            logical index is hidden.

        """
        raise NotImplementedError

    def logicalIndex(self, visual_index):
        """ Get the logical index for a given visual index.

        Parameters
        ----------
        visual_index : int
            The visual header index to map to a model logical index.
            This must be bounded by zero and the header count.

        Returns
        -------
        result : int
            The logical model index for the visual header index.

        """
        raise NotImplementedError

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def paintEvent(self, event):
        """ A reimplemented virtual method.

        This paint event handler will dispatch to `paintHorizontal` or
        `paintVertical` depending on the orientation of the header.

        """
        painter = QPainter(self)
        try:
            if self._orientation == Qt.Horizontal:
                self.paintHorizontal(painter, event)
            else:
                self.paintVertical(painter, event)
        except Exception:
            painter.end()
            raise

    def paintHorizontal(self, painter, event):
        """ The default horizontal header paint method.

        This paint method will render the header as a single row of
        header sections. Subclasses which need to perform custom
        painting may reimplement this method.

        Parameters
        ----------
        painter : QPainter
            The painter to use for drawing the header.

        event : QPaintEvent
            The paint event passed to the `paintEvent` method.

        """
        # The cell rect is updated during iteration. Only a single rect
        # object is allocated for the entire paint event.
        cell_rect = QRect()

        # The grid line is updated during iteration. Only a single line
        # object is allocated for the entire paint event.
        grid_line = QLine()

        # Prefetch common data for faster access.
        height = self.height()
        font_metrics = self.fontMetrics()

        for rect in event.region().rects():

            # Compute the index bounds of the dirty rect.
            x1 = rect.x()
            x2 = x1 + rect.width()
            first_visual_col = self.visualIndexAt(x1 + self._offset)
            last_visual_col = self.visualIndexAt(x2 + self._offset)

            # If the first is out of bounds, there is nothing to draw.
            if first_visual_col == -1:
                continue

            # Set the clip rect to avoid overdrawing onto other parts
            # of the region. This is crucial to elimination overdrawing
            # of antialiased fonts when scrolling one pixel at a time.
            painter.setClipRect(rect)

            # If the last is out bounds, clip to the last valid index.
            if last_visual_col == -1:
                last_visual_col = self.count() - 1

            # Compute the column indices, data, and paint start position.
            col_widths = []
            col_indices = []
            for idx in xrange(first_visual_col, last_visual_col + 1):
                col_widths.append(self.sectionSize(idx))
                col_indices.append(self.logicalIndex(idx))
            data = iter(self._model.column_header_data(col_indices))
            start_x = self.sectionPosition(first_visual_col) - self._offset

            # Fill the entire invalid rect with the background gradient.
            max_x = start_x + sum(col_widths) - 1
            if rect.right() > max_x:
                rect.setRight(max_x)
            painter.fillRect(rect, self._gradient)

            # Draw the text for each header section.
            x_run = start_x

            try:
                next_data = data.next
                if self._elide_mode == Qt.ElideNone:
                    for col_width in col_widths:
                        cell_rect.setRect(x_run, 0, col_width, height)
                        painter.drawText(cell_rect, Qt.AlignCenter, next_data())
                        x_run += col_width
                else:
                    elide_mode = self._elide_mode
                    for col_width in col_widths:
                        cell_rect.setRect(x_run, 0, col_width, height)
                        text = font_metrics.elidedText(next_data(), elide_mode, col_width - 4)
                        painter.drawText(cell_rect, Qt.AlignCenter, text)
                        x_run += col_width
            except StopIteration: # ran out of data early
                pass

            # Save the painter state since pens will be switched.
            painter.save()

            # Draw the white line at the left edge of each section.
            # XXX make configurable.
            painter.setPen(Qt.white)
            x_run = start_x
            for col_width in col_widths:
                grid_line.setLine(x_run, 0, x_run, height)
                painter.drawLine(grid_line)
                x_run += col_width

            # Draw the gray line at the right edge of each section.
            # XXX make configurable.
            painter.setPen(Qt.gray)
            x_run = start_x
            for col_width in col_widths:
                x_run += col_width
                grid_line.setLine(x_run - 1, 0, x_run - 1, height)
                painter.drawLine(grid_line)

            # Draw the gray line at the bottom of the sections.
            grid_line.setLine(x1, height - 1, max_x, height - 1)
            painter.drawLine(grid_line)

            # Restore the painter state for the next loop iteration.
            painter.restore()

    def paintVertical(self, painter, event):
        """ The default vertical header paint method.

        This paint method will render the header as a single row of
        header sections. Subclasses which need to perform custom
        painting may reimplement this method.

        Parameters
        ----------
        painter : QPainter
            The painter to use for drawing the header.

        event : QPaintEvent
            The paint event passed to the `paintEvent` method.

        """
        # The cell rect is updated during iteration. Only a single rect
        # object is allocated for the entire paint event.
        cell_rect = QRect()

        # The grid line is updated during iteration. Only a single line
        # object is allocated for the entire paint event.
        grid_line = QLine()

        # Prefetch common data for faster access.
        width = self.width()
        font_metrics = self.fontMetrics()

        for rect in event.region().rects():

            # Compute the index bounds of the dirty rect.
            y1 = rect.y()
            y2 = y1 + rect.height()
            first_visual_row = self.visualIndexAt(y1 + self._offset)
            last_visual_row = self.visualIndexAt(y2 + self._offset)

            # If the first is out of bounds, there is nothing to draw.
            if first_visual_row == -1:
                continue

            # Set the clip rect to avoid overdrawing onto other parts
            # of the region. This is crucial to elimination overdrawing
            # of antialiased fonts when scrolling one pixel at a time.
            painter.setClipRect(rect)

            # If the last is out bounds, clip to the last valid index.
            if last_visual_row == -1:
                last_visual_row = self.count() - 1

            # Compute the column indices, data, and paint start position.
            row_heights = []
            row_indices = []
            for idx in xrange(first_visual_row, last_visual_row + 1):
                row_heights.append(self.sectionSize(idx))
                row_indices.append(self.logicalIndex(idx))
            data = iter(self._model.row_header_data(row_indices))
            start_y = self.sectionPosition(first_visual_row) - self._offset

            # Fill each invalid section with the background gradient.
            grad = self._gradient
            y_run = start_y
            for row_height in row_heights:
                cell_rect.setRect(0, y_run, width, row_height)
                painter.fillRect(cell_rect, grad)
                y_run += row_height

            # Draw the text for each header section.
            y_run = start_y
            try:
                next_data = data.next
                if self._elide_mode == Qt.ElideNone:
                    for row_height in row_heights:
                        cell_rect.setRect(0, y_run, width, row_height)
                        painter.drawText(cell_rect, Qt.AlignCenter, next_data())
                        y_run += row_height
                else:
                    elide_mode = self._elide_mode
                    for row_height in row_heights:
                        cell_rect.setRect(0, y_run, width, row_height)
                        text = font_metrics.elidedText(next_data(), elide_mode, width-4)
                        painter.drawText(cell_rect, Qt.AlignCenter, text)
                        y_run += row_height
            except StopIteration: # ran out of data early
                pass

            max_y = start_y + sum(row_heights) - 1

            # Save the painter state since pens will be switched.
            painter.save()

            # Draw the white line at the left edge of the sections.
            # XXX make configurable.
            painter.setPen(Qt.white)
            grid_line.setLine(0, y1, 0, max_y)
            painter.drawLine(grid_line)

            # Draw the gray line at the right edge of the sections.
            # XXX make configurable.
            painter.setPen(Qt.gray)
            grid_line.setLine(width - 1, y1, width - 1, max_y)
            painter.drawLine(grid_line)

            # Draw the gray line at the bottom edge of each section.
            # XXX make configurable.
            y_run = start_y
            for row_height in row_heights:
                y_run += row_height
                grid_line.setLine(0, y_run - 1, width, y_run - 1)
                painter.drawLine(grid_line)

            # Restore the painter state for the next loop iteration.
            painter.restore()

