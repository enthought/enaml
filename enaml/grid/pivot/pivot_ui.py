#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from __future__ import absolute_import

import os

import numpy as np
from enaml.qt.qt.QtCore import Qt, QObject, QModelIndex, Signal, QSize, QRect, QLine
from enaml.qt.qt.QtGui import (
        QColor, QBrush, QStyleOptionHeader, QStyle,
        QMenu, QAction, QApplication, QCursor, QRegion, QPixmap, QIcon,
        QFont, QFontMetrics, QPalette, QTableView, QFrame,
        )

from ..q_tabular_view import QTabularView
from ..q_tabular_header import QTabularHeader
from ..tabular_model import TabularModel
from .pandas_pivot import MarginNode, AggregationNode, format_aggregate

# Just an invalid QModelIndex for those places that we need it.
dummy_index = QModelIndex()

# The foreground color of the AggregationNodes
AGGREGATION_FG_BRUSH = QBrush(QColor("blue"))

def localfile(*pathparts):
    return os.path.join(os.path.dirname(__file__), *pathparts)

icon_files = {
    'expand': localfile('images', 'toggle-small-expand.png'),
    'collapse': localfile('images', 'toggle-small.png'),
}


class UniqueCache(dict):
    """ Map unique integers to objects.

    This can be used for temporary caches where we need a quick, ad hoc mapping
    from primitive types (like ints) to objects. This can be used to pass
    a "reference" to a Python object to Qt and look it up again once the user
    has selected something.
    """
    def __init__(self):
        super(UniqueCache, self).__init__()

        self._count = 0

    def store(self, value):
        """ Store a value in the cache and return its key.
        """
        self._count += 1
        self[self._count] = value
        return self._count


class PivotModel(TabularModel):
    def __init__(self, engine):
        super(PivotModel, self).__init__()
        self.engine = engine
        self._make_depth_color_table()
        self.shape = self.engine.shape
        self.engine.on_trait_change(self._update_structure, 'update')

    def row_count(self):
        return self.shape[0]

    def column_count(self):
        return self.shape[1]

    # This isn't used
    def column_header_data(self, columns):
        return []

    # This isn't used
    def row_header_data(self, rows):
        return []

    def data(self, rows, columns):
        data = []
        for row in rows:
            for column in columns:
                val = self.engine.data(row, column)
                data.append(self.engine.format_value(val))
        return data

    def _update_structure(self, new):
        """ Handle the structure changed event.
        """
        axis, event = new
        if axis == 'rows':
            return self._change_rows(event)
        elif axis == 'cols':
            return self._change_cols(event)

        # If we get to here, then we don't have any special handling. Just reset
        # the whole model.
        #self.beginResetModel()
        self.shape = self.engine.shape
        #self.endResetModel()

    def _change_rows(self, event):
        """ Change the given rows.
        """
        i, j = event.old_span
        k = i + len(event.new_leaves)
        # For the rows that are present before and after, just tell Qt to update
        # their data.
        if j < k:
            # We have new rows.
            #self.beginInsertRows(dummy_index, j, k-1)
            self.shape = self.engine.shape
            #self.endInsertRows()
        elif j > k:
            # We have fewer rows.
            #self.beginRemoveRows(dummy_index, k, j-1)
            self.shape = self.engine.shape
            #self.endRemoveRows()
        self._rows_data_changed(i, min(j, k)-1)

    def _change_cols(self, event):
        """ Change the given columns.
        """
        i, j = event.old_span
        k = i + len(event.new_leaves)
        # For the columns that are present before and after, just tell Qt to
        # update their data.
        if j < k:
            # We have new columns.
            #self.beginInsertColumns(dummy_index, j, k-1)
            self.shape = self.engine.shape
            #self.endInsertColumns()
        elif j > k:
            # We have fewer columns.
            #self.beginRemoveColumns(dummy_index, k, j-1)
            self.shape = self.engine.shape
            #self.endRemoveColumns()
        self._cols_data_changed(i, min(j, k)-1)

    def _rows_data_changed(self, first, last):
        """ Signal that the data of the given rows have changed.
        """
        #top_left = self.index(first, 0)
        #bottom_right = self.index(last, self.shape[1])
        #self.dataChanged.emit(top_left, bottom_right)
        #self.headerDataChanged.emit(Qt.Vertical, first, last)
        self.dataChanged.emit()
        self.verticalHeaderChanged.emit()

    def _cols_data_changed(self, first, last):
        """ Signal that the data of the given columns have changed.
        """
        #top_left = self.index(0, first)
        #bottom_right = self.index(self.shape[0], last)
        #self.dataChanged.emit(top_left, bottom_right)
        #self.headerDataChanged.emit(Qt.Horizontal, first, last)
        self.dataChanged.emit()
        self.horizontalHeaderChanged.emit()

    # XXX None of the rest works as yet

    def data1(self, index, role):
        if role == Qt.DisplayRole:
            x = self.engine.data(index.row(), index.column())
            return self.engine.format_value(x)
        elif role == Qt.BackgroundRole and self.engine.shade_depth:
            depth = self.engine.fold_depth(index.row(), index.column())
            return self.depth_color_table[depth]
        elif role == Qt.ToolTipRole:
            agg_column, agg_func, row_path, col_path = self.engine.get_path_to_cell(
                index.row(), index.column())
            return u'{0} - {1}\n{2}'.format(agg_column, agg_func,
                '\n'.join('{0}: {1}'.format(col, val) for col, val in row_path+col_path))
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignRight
        return None

    def _make_depth_color_table(self):
        """ Make a color table for showing the aggregation depth by
        background shading.
        """
        # Slightly modified Blues colormap from ColorBrewer.
        base_red, base_green, base_blue = np.array([
            [1.0, 1.0, 1.0],
            [0.87058823529399998, 0.92156862745099999, 0.96862745098000003],
            [0.77647058823500004, 0.85882352941200002, 0.93725490196100003],
            [0.61960784313700001, 0.79215686274499997, 0.88235294117600005],
            [0.419607843137, 0.68235294117599998, 0.83921568627499998],
            [0.25882352941199999, 0.57254901960799998, 0.77647058823500004],
            #[0.12941176470599999, 0.44313725490200001, 0.70980392156899996],
            #[0.031372549019600002, 0.31764705882400002, 0.61176470588200005],
            #[0.031372549019600002, 0.188235294118, 0.419607843137],
        ]).transpose()
        x = np.linspace(0.0, 1.0, self.engine.max_depth + 1)
        xp = np.linspace(0.0, 1.0, len(base_red))
        red = np.interp(x, xp, base_red)
        green = np.interp(x, xp, base_green)
        blue = np.interp(x, xp, base_blue)
        self.depth_color_table = [
            QBrush(QColor.fromRgbF(red[i], green[i], blue[i]))
            for i in range(len(red))]



class MultiLevelHeader(QTabularHeader):
    """ A hierarchical header for viewing dynamic pivot tables.
    """

    # Class-level cache of QIcons.
    icon_cache = {}

    # Ensure that the given row/column is visible.
    ensure_visible = Signal(int, name='ensure_visible')

    def __init__(self, engine, orientation, parent=None):
        self.engine = engine
        self.is_horizontal = (orientation == Qt.Horizontal)
        if self.is_horizontal:
            self.header_model = self.engine.col_header
            self.engine.on_trait_change(self._update_header_model, 'col_header')
            self.engine.on_trait_change(lambda: self.update(), 'col_header:update')
        else:
            self.header_model = self.engine.row_header
            self.engine.on_trait_change(self._update_header_model, 'row_header')
            self.engine.on_trait_change(lambda: self.update(), 'row_header:update')
        super(MultiLevelHeader, self).__init__(orientation, parent)

        self.engine.on_trait_change(self._clear_cursor, 'update')
        self.cursor_waiting = False
        self.cursor_callback = None

        self.icon_position_cache = {}
        self.cell_rect_cache = {}
        self.cell_size_cache = {}

    def mousePressEvent(self, event):
        """ Override to handle clicks on the expand/collapse icons.
        """
        mouse_pos = event.pos()
        mouse_button = event.button()
        node = self._get_node_for_position(mouse_pos)
        if mouse_button == Qt.LeftButton:
            if node in self.icon_position_cache:
                icon_rect = self.icon_position_cache[node]
                if icon_rect.contains(mouse_pos):
                    toggled = self._toggle_node(node)
                    if toggled:
                        event.accept()
                        return
        return super(MultiLevelHeader, self).mousePressEvent(event)

    def _get_node_for_position(self, mouse_pos):
        """ Return the Node for a given mouse position relative to the HeaderView.

        Return None if there is not one found.
        """
        pos = mouse_pos.x() if self.is_horizontal else mouse_pos.y()
        section = self.visualIndexAt(pos+self._offset)
        for node in self._get_nodes_for_section(section):
            rect = self.cell_rect_cache.get(node, None)
            if rect is not None and rect.contains(mouse_pos):
                return node
        return None

    def _get_leaf_node(self, section):
        """ Get the leaf node for a section.
        """
        return self.header_model.leaves[section]

    def _get_nodes_for_section(self, section):
        """ Get all of the nodes displayed in the section, starting at the top.
        """
        leaf = self.header_model.leaves[section]
        return leaf.ancestors() + [leaf]

    def _toggle_node(self, node):
        """ Toggle the expanded state of a node, if possible.

        Return True if the node was actually toggled.
        """
        # FIXME: The order of events is a little convoluted here. In the
        # synchronous case, setting the .expanded trait on the Node will issue
        # the update event that clears the cursor. Consequently, we need to set
        # the wait cursor before we even try to set the .expanded trait.
        # FIXME: should set some kind of timeout to show some kind of error if
        # we don't get a response in time.
        toggled = False
        self.cursor_waiting = True
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        if node.expanded:
            # Collapse the Node.
            self.cursor_callback = lambda: self._scroll_to_node(node)
            node.expanded = False
            toggled = True
        elif len(node.children) > 0:
            # Expand the Node.
            node.expanded = True
            toggled = True
        # Otherwise, clear the cursor that we set.
        if not toggled:
            self._clear_cursor()
        return toggled

    def _clear_cursor(self):
        """ Clear the wait cursor if it's around.
        """
        if self.cursor_waiting:
            QApplication.restoreOverrideCursor()
            self.cursor_waiting = False
        if self.cursor_callback is not None:
            self.cursor_callback()
            self.cursor_callback = None

    def _scroll_to_node(self, node):
        """ Scroll the table's viewport to make sure the given Node is visible.
        """
        # Find the Node's location and make sure that we scroll to make it
        # visible. Otherwise, it will look confusing.
        i = self.header_model.span_left[node]
        self.ensure_visible.emit(i)

    def _get_icon(self, name):
        """ Return a QIcon for the given name.
        """
        if name not in self.icon_cache:
            if name == 'transparent':
                pixmap = QPixmap(16, 16)
                pixmap.fill(Qt.transparent)
                self.icon_cache[name] = QIcon(pixmap)
            else:
                self.icon_cache[name] = QIcon(icon_files[name])
        return self.icon_cache[name]

    #--------------------------------------------------------------------------
    # Abstract API implementation.
    #--------------------------------------------------------------------------
    def count(self):
        """ Get the number of visible sections in the header.

        This count does not include hidden sections.

        Returns
        -------
        result : int
            The number of visible sections in the header.

        """
        if self.is_horizontal:
            count = self._model.column_count()
        else:
            count = self._model.row_count()
        return count

    def length(self):
        """ Get the total visible length of the header.

        This length does not include hidden sections.

        Returns
        -------
        result : int
            The total visible length of the header.

        """
        return sum(self.sectionSize(i) for i in range(self.count()))

    def headerSize(self):
        """ Get the display size for the header.

        Returns
        -------
        result : int
            The size to use by QTabularView when displaying the header.
            For horizontal headers, this will be the header height. For
            vertical headers, this will be the header width.

        """
        if self.count():
            if self.is_horizontal:
                size = max(*(self.sectionSizeFromContents(i).height() for i in range(self.count())))
            else:
                size = max(*(self.sectionSizeFromContents(i).width() for i in range(self.count())))
        else:
            size = 0
        return size

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
        logical_index = self.logicalIndex(visual_index)
        size = self.sectionSizeFromContents(logical_index)
        return size.width() if self.is_horizontal else size.height()

    def sectionSizeFromContents(self, logical_index):
        leaf = self._get_leaf_node(logical_index)
        opt = QStyleOptionHeader(self._style_option(leaf, logical_index))
        # FIXME: this reuses the same style option from the leaf for all of the
        # nodes. If the icon on the leaf is a different size or is absent, the
        # sizes will be wrong.
        size = QSize(self._cell_size(leaf.text, opt))
        for node in leaf.ancestors():
            if self.is_horizontal:
                size.setHeight(size.height() + self._cell_size(node.text, opt).height())
            else:
                size.setWidth(size.width() + self._cell_size(node.text, opt).width())
        return size

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
        return sum(self.sectionSize(i) for i in range(visual_index))

    def trailingSpan(self, length):
        """ Get the number of trailing items covered by a given length.

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
        # This is broken - assumes constant section size
        return length / self.sectionSize(0)

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
        # This is broken - assumes constant section size
        idx = position / self.sectionSize(0)
        if idx < self.count():
            return idx
        return -1

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
        # XXX section moving and hiding not yet supported
        return logical_index

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
        # XXX section moving and hiding not yet supported.
        return visual_index

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
            start_x = self.sectionPosition(first_visual_col) - self._offset

            # Draw the text for each header section.
            x_run = start_x
            col = first_visual_col
            try:
                for col_width in col_widths:
                    cell_rect.setRect(x_run, 0, col_width, height)
                    self.paintSection(painter, cell_rect, col)
                    x_run += col_width
                    col += 1
            except StopIteration: # ran out of data early
                pass

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
            start_y = self.sectionPosition(first_visual_row) - self._offset

            # Draw the text for each header section.
            y_run = start_y
            try:
                row = first_visual_row
                for row_height in row_heights:
                    cell_rect.setRect(0, y_run, width, row_height)
                    self.paintSection(painter, cell_rect, row)
                    y_run += row_height
                    row += 1
            except StopIteration: # ran out of data early
                pass

    def paintSection(self, painter, rect, logical_index):
        """ Paint a header section.
        """
        if rect.isValid():
            leaf = self._get_leaf_node(logical_index)
            if self.is_horizontal:
                line = rect.y()
            else:
                line = rect.x()
            for node in self._get_nodes_for_section(logical_index):
                opt = self._style_option(node, logical_index)
                args = (node, leaf, painter, rect, logical_index, opt, line)
                if self.is_horizontal:
                    line = self._paint_horizontal_cell(*args)
                else:
                    line = self._paint_vertical_cell(*args)
            return

    def _paint_horizontal_cell(self, node, leaf, painter, rect, logical_index, opt, top):
        """ Paint a cell in a horizontal header.
        """
        # Make our own copy.
        opt = QStyleOptionHeader(opt)
        height = self._cell_size(node.text, opt).height()
        if node is leaf:
            height = rect.height() - top
        left = self._current_cell_left(node, leaf, rect.left())
        width = self._current_cell_width(node)

        opt.rect = QRect(left, top, width, height)
        self._paint_cell(node, opt, painter, rect)
        return top + height

    def _paint_vertical_cell(self, node, leaf, painter, rect, logical_index, opt, left):
        """ Paint a cell in a vertical header.
        """
        # Make our own copy.
        opt = QStyleOptionHeader(opt)
        width = self._cell_size(node.text, opt).width()
        if node is leaf:
            width = rect.width() - left
        top = self._current_cell_left(node, leaf, rect.top())
        height = self._current_cell_width(node)

        opt.rect = QRect(left, top, width, height)
        self._paint_cell(node, opt, painter, rect)
        return left + width

    def _paint_cell(self, node, opt, painter, rect):
        """ Common cell-painting code.
        """
        self.cell_rect_cache[node] = QRect(opt.rect)
        # Limit the drawing of the label to the viewport.
        # XXX opt.rect &= (opt.rect & self.viewport().geometry()).united(rect)

        style = self.style()
        self._set_foreground_brush(opt, node)
        self._set_background_brush(opt, node)
        text = node.text
        #elide_mode = self.textElideMode()
        #if elide_mode != Qt.ElideNone:
        #    decoration_size = style.sizeFromContents(style.CT_HeaderSection,
        #        opt, QSize(), self)
        #    text = opt.fontMetrics.elidedText(text, elide_mode,
        #        opt.rect.width() - decoration_size.width())
        opt.text = text
        painter.save()
        old_brush_origin = painter.brushOrigin()
        painter.setBrushOrigin(opt.rect.topLeft())

        # Draw the background.
        clip_region = painter.clipRegion()
        painter.setClipRect(rect & opt.rect)
        style.drawControl(style.CE_HeaderSection, opt, painter, self)

        # Draw the label.
        subopt = QStyleOptionHeader(opt)
        subopt.rect = style.subElementRect(style.SE_HeaderLabel, opt, self)
        if subopt.rect.isValid() and not (rect & subopt.rect).isEmpty():
            self._paint_cell_label(painter, subopt, node, rect)
        else:
            # If we paint the cell but not the label, remove the icon position
            # from the cache. We don't want to cache any geometry that we don't
            # display.
            self.icon_position_cache.pop(node, None)
        if opt.sortIndicator != QStyleOptionHeader.None:
            subopt.rect = style.subElementRect(style.SE_HeaderArrow, opt, self)
            if subopt.rect.isValid() and not (rect & subopt.rect).isEmpty():
                style.drawPrimitive(style.PE_IndicatorHeaderArrow, subopt, painter, self)
        painter.setClipRegion(clip_region)

        painter.setBrushOrigin(old_brush_origin)
        painter.restore()

    def _paint_cell_label(self, painter, opt, node, section_rect):
        """ Paint the label of the cell with the icon correctly placed.
        """
        style = self.style()
        rect = QRect(opt.rect)

        # Draw the icon.
        pixmap_side = style.pixelMetric(QStyle.PM_SmallIconSize)
        pixmap_size = QSize(pixmap_side, pixmap_side)
        aligned_rect = style.alignedRect(Qt.LeftToRight,
            opt.iconAlignment, pixmap_size, rect)
        inter = aligned_rect & rect
        if not (inter & section_rect).isEmpty():
            pixmap = opt.icon.pixmap(pixmap_size, QIcon.Normal)
            painter.drawPixmap(inter.x(), inter.y(), pixmap,
                inter.x() - aligned_rect.x(), inter.y() - aligned_rect.y(),
                inter.width(), inter.height())
        rect.setLeft(rect.left() + pixmap_side)
        # Store the rect of the drawn pixmap in the cache so it can be used
        # for hit-testing.
        self.icon_position_cache[node] = inter

        font = QFont(painter.font())
        if opt.state & style.State_On or isinstance(node, MarginNode):
            font.setBold(True)
            painter.setFont(font)
        fm = QFontMetrics(font)
        text_size = fm.size(0, opt.text)

        aligned_rect = style.alignedRect(Qt.LeftToRight,
            opt.textAlignment, text_size, rect)
        if not (aligned_rect & section_rect).isEmpty():
            style.drawItemText(painter, rect, opt.textAlignment, opt.palette,
                (opt.state & style.State_Enabled), opt.text, opt.palette.ButtonText)

    # XXX DONE

    def _current_cell_width(self, node):
        """ Get the current cell width.

        Add up the section sizes corresponding to all of the leaves.
        """
        return sum(self.sectionSize(i) for i in range(*self._get_span(node)))

    def _current_cell_left(self, node, leaf, left):
        """ Get the left side of the given cell.
        """
        leaf_section = self.header_model.leaves.index(leaf)
        span = self._get_span(node)
        for section in range(leaf_section-1, span[0]-1, -1):
            left -= self.sectionSize(section)
        return left

    def _cell_size(self, text, opt):
        """ Return the size for the given cell.
        """
        if text not in self.cell_size_cache:
            size = QSize()
            font = QFont(self.font())
            font.setBold(True)
            fm = QFontMetrics(font)
            data_size = fm.size(0, text)
            decoration_size = self.style().sizeFromContents(
                QStyle.CT_HeaderSection, opt, QSize(), self)
            size = QSize(data_size.width() + decoration_size.width(),
                max(data_size.height(), decoration_size.height()))
            self.cell_size_cache[text] = size
        return self.cell_size_cache[text]

    def _style_option(self, node, section):
        """ Configure the style option for the given section.
        """
        opt = QStyleOptionHeader()
        # XXX self.initStyleOption(opt)
        if self.window().isActiveWindow():
            opt.state |= QStyle.State_Active

        opt.textAlignment = Qt.AlignLeft | Qt.AlignTop
        opt.iconAlignment = Qt.AlignLeft | Qt.AlignTop
        opt.section = section

        if node.expanded:
            opt.icon = self._get_icon('collapse')
        elif len(node.children) > 0:
            opt.icon = self._get_icon('expand')
        else:
            # FIXME: the rest of the sizing code depends on every cell having
            # the same sized icon.
            opt.icon = self._get_icon('transparent')

        # Determine if the section is visually at the beginning, the end, both, or neither.
        visual = self.visualIndex(section)
        count = self.count()
        if count == 1:
            opt.position = QStyleOptionHeader.OnlyOneSection
        elif visual == 0:
            opt.position = QStyleOptionHeader.Beginning
        elif visual == count - 1:
            opt.position = QStyleOptionHeader.End
        else:
            opt.position = QStyleOptionHeader.Middle

        return opt

    def _set_foreground_brush(self, opt, node):
        if isinstance(node, AggregationNode):
            opt.palette.setBrush(QPalette.ButtonText, AGGREGATION_FG_BRUSH)

    def _set_background_brush(self, opt, node):
        return
#        brush = cell_index.data(Qt.BackgroundRole);
#        if brush is not None:
#            opt.palette.setBrush(QPalette.Button, brush)
#            opt.palette.setBrush(QPalette.Window, brush)

    def _get_span(self, node):
        """ Return the [left, right) span of the node.
        """
        return (self.header_model.span_left[node],
            self.header_model.span_right[node]+1)

#   def _on_section_resized(self, logical_index, old_size, new_size):
#       """ Repaint all of the affected sections.
#       """
#       sections = self._related_sections(logical_index)
#       viewport = self.viewport()
#       w = viewport.width()
#       h = viewport.height()
#       pos = min(self.sectionViewportPosition(section) for section in sections)
#       if self.is_horizontal:
#           r = QRect(pos, 0, w-pos, h)
#       else:
#           r = QRect(0, pos, w, h-pos)
#       viewport.update(r.normalized())

    def _update_header_model(self, new):
        self.header_model = new
        self.update()



def table_view(engine, highlight_sections=False, model_class=PivotModel,
    view_class=QTabularView, header_class=MultiLevelHeader, parent=None):
    """ Return a QTabularView configured to display a PandasEngine.
    """
    model = model_class(engine)

    tv = view_class(parent)

    hhv = header_class(engine, Qt.Horizontal, parent=tv)
    #hhv.setHighlightSections(highlight_sections)
    #hhv.setClickable(True)
    #hhv.setDefaultSectionSize(120)
    tv.setColumnHeader(hhv)

    # Hook up to the "ensure_visible" signal to scroll to the right column.
    #def _col_ensure_visible(column):
    #    idx = model.createIndex(tv.rowAt(1), column)
    #    tv.scrollTo(idx)
    #hhv.ensure_visible.connect(_col_ensure_visible)

    vhv = header_class(engine, Qt.Vertical, parent=tv)
    #vhv.setHighlightSections(highlight_sections)
    #vhv.setClickable(True)
    tv.setRowHeader(vhv)

    # Hook up to the "ensure_visible" signal to scroll to the right row.
    #def _row_ensure_visible(row):
    #    idx = model.createIndex(row, tv.columnAt(1))
    #    tv.scrollTo(idx)
    #vhv.ensure_visible.connect(_row_ensure_visible)

    tv.setModel(model)
    tv._debug_draw_regions = False
    #tv.setSelectionMode(tv.ContiguousSelection)
    #tv.resizeRowsToContents()

    return tv
