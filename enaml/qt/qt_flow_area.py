#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt, QSize, QRect
from .qt.QtGui import QScrollArea, QFrame, QLayout, QWidgetItem
from .qt_constraints_widget import QtConstraintsWidget
from .qt_flow_item import QtFlowItem, QFlowItem


_ALIGN_MAP = {
    'leading': Qt.AlignLeading,
    'trailing': Qt.AlignTrailing,
    'center': Qt.AlignCenter,
}


_ORIENTATION_MAP = {
    'horizontal': Qt.Horizontal,
    'vertical': Qt.Vertical,
}


class QFlowLayout(QLayout):
    """ A custom QLayout which implements a flow layout.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a QFlowLayout.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a QLayout.

        """
        super(QFlowLayout, self).__init__(*args, **kwargs)
        self._items = []
        self._alignment = Qt.AlignLeading
        self._orientation = Qt.Horizontal
        self._reverse_fill = False
        self._cached_w = -1
        self._cached_hfw = -1
        self._cached_min = None
        self._v_spacing = 10
        self._h_spacing = 10
        self._wfh_size = None

    def addWidget(self, widget):
        """ Add a widget to the end of the flow layout.

        Parameters
        ----------
        widget : QFlowWidget
            The flow widget to add to the layout.

        """
        self.insertWidget(self.count(), widget)

    def insertWidget(self, index, widget):
        """ Insert a widget into the flow layout.

        Parameters
        ----------
        index : int
            The index at which to insert the widget.

        widget : QFlowWidget
            The flow widget to insert into the layout.

        """
        assert isinstance(widget, QFlowItem), 'invalid widget type'
        self.addChildWidget(widget)
        self._items.insert(index, QWidgetItem(widget))
        widget.show()
        self.invalidate()

    def alignment(self):
        """ Get the edge alignment for the items the layout.

        Returns
        -------
        result : enum
            The edge alignment of the layout items. This must be one of
            Qt.AlignLeading, Qt.AlignTrailing, or Qt.AlignCenter.

        """
        return self._alignment

    def setAlignment(self, alignment):
        """ Set the edge alignment for the items in the layout.

        Parameters
        ----------
        alignment : enum
            The edge alignment for the layout items, either Qt.AlignLeft
            or Qt.AlignRight.

        """
        allowed = (Qt.AlignLeading, Qt.AlignTrailing, Qt.AlignCenter)
        assert alignment in allowed, 'invalid alignment'
        self._alignment = alignment
        self.invalidate()

    def orientation(self):
        """ Get the orientation of the flow layout.

        Returns
        -------
        result : enum
            The orientation of the layout, either Qt.Horizontal or
            Qt.Vertical. The default is Qt.Horizontal.

        """
        return self._orientation

    def setOrientation(self, orientation):
        """ Set the orientation of the flow layout.

        Parameters
        ----------
        orientation : enum
            The orientation of the layout, either Qt.Horizontal or
            Qt.Vertical.

        """
        allowed = (Qt.Horizontal, Qt.Vertical)
        assert orientation in allowed, 'invalid orientation'
        self._orientation = orientation
        self.invalidate()

    def reverseFill(self):
        """ Get whether reverse fill is enabled for this layout.

        Returns
        -------
        result : bool
            True if reverse fill is enabled, False otherwise. The
            default is False.

        """
        return self._reverse_fill

    def setReverseFill(self, enable):
        """ Set whether reverse fill is enabled for this layout.

        Parameters
        ----------
        enable : bool
            Whether or not to enable reverse fill.

        """
        self._reverse_fill = enable
        self.invalidate()

    def horizontalSpacing(self):
        """ Get the horizontal spacing for the layout.

        Returns
        -------
        result : int
            The number of pixels of horizontal space between columns in
            the layout. The default is 10px.

        """
        return self._h_spacing

    def setHorizontalSpacing(self, spacing):
        """ Set the horizontal spacing for the layout.

        Parameters
        ----------
        spacing : int
            The number of pixels of horizontal space to place between
            columns in the layout.

        """
        self._h_spacing = spacing
        self.invalidate()

    def verticalSpacing(self):
        """ Get the vertical spacing for the layout.

        Returns
        -------
        result : int
            The number of pixels of vertical space between rows in the
            layout. The default is 10px.

        """
        return self._v_spacing

    def setVerticalSpacing(self, spacing):
        """ Set the vertical spacing for the layout.

        Parameters
        ----------
        spacing : int
            The number of pixels of vertical space to place between
            rows in the layout.

        """
        self._v_spacing = spacing
        self.invalidate()

    def hasHeightForWidth(self):
        """ Whether the height of the layout depends on its width.

        Returns
        -------
        result : bool
            True if the flow direction is horizontal, False otherwise.

        """
        return self._orientation == Qt.Horizontal

    def heightForWidth(self, width):
        """ Get the height of the layout for the given width.

        This value only has meaning if the flow direction is horizontal.

        Parameters
        ----------
        width : int
            The width for which to determine a height.

        """
        if self._cached_w != width:
            left, top, right, bottom = self.getContentsMargins()
            adj_width = width - (left + right)
            self._cached_w = adj_width
            h = self._doLayout(QRect(left, 0, adj_width, 0), True)
            self._cached_hfw = h + top + bottom
        return self._cached_hfw

    def addItem(self, item):
        """ A required virtual method implementation.

        This method should not be used. The methods `addWidget` and
        `insertWidget` should be used instead.

        """
        msg = 'Use `addWidget` and `insertWidget` instead.'
        raise NotImplementedError(msg)

    def invalidate(self):
        """ Invalidate the cached values of the layout.

        """
        self._cached_w = -1
        self._cached_hfw = -1
        self._cached_min = None
        self._wfh_size = None
        super(QFlowLayout, self).invalidate()

    def count(self):
        """ A virtual method implementation which returns the number of
        items in the layout.

        """
        return len(self._items)

    def itemAt(self, idx):
        """ A virtual method implementation which returns the layout item
        for the given index or None if one does not exist.

        """
        items = self._items
        if idx < len(items):
            return items[idx]

    def takeAt(self, idx):
        """ A virtual method implementation which removes and returns the
        item at the given index or None if one does not exist.

        """
        items = self._items
        if idx < len(items):
            item = items[idx]
            del items[idx]
            item.widget().hide()
            return item

    def sizeHint(self):
        """ A virtual method implementation which returns the size hint
        for the layout.

        For a flow layout, the size hint is equivalent to the minimum
        size.

        """
        return self.minimumSize()

    def setGeometry(self, rect):
        """ Sets the geometry of all the items in the layout.

        """
        super(QFlowLayout, self).setGeometry(rect)
        self._doLayout(self.contentsRect())

    def minimumSize(self):
        """ A reimplemented method which returns the minimum size hint
        of the layout item widget as the minimum size of the window.

        """
        if self._cached_min is None:
            size = QSize(0, 0)
            for item in self._items:
                size = size.expandedTo(item.sizeHint())
            left, top, right, bottom = self.getContentsMargins()
            size.setWidth(size.width() + left + right)
            size.setHeight(size.height() + top + bottom)
            self._cached_min = size
        if self._orientation == Qt.Vertical:
            s = self._wfh_size or QSize(0, 0)
            return s.expandedTo(self._cached_min)
        return self._cached_min

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _doLayout(self, rect, test=False):
        """ Perform the layout for the given rect.

        Parameters
        ----------
        rect : QRect
            The area to use for performing the layout.

        test : bool, optional
            If True, perform a trial run of the layout without actually
            updating any of the item geometries.

        Returns
        -------
        result : int
            The layout space required in the direction opposite of the
            layout flow.

        """
        if self._orientation == Qt.Vertical:
            res = self._doVerticalLayout(rect, test)
            s = rect.size()
            s.setWidth(res)
            self._wfh_size = s
        else:
            res = self._doHorizontalLayout(rect, test)
        return res

    def _doHorizontalLayout(self, rect, test):
        """ Perform the layout for a horizontal orientation.

        The method signature is identical to the `_doLayout` method.

        """
        rect_left = rect.x()
        rect_right = rect_left + rect.width()

        # This loop passes over the list of items and separates them
        # into individual rows. A given item is allowed to overflow a
        # row if it is the only member of the row. An item at the end
        # of  a populated row which overflows is moved to the next line.
        # The total width and height of a row is kept as a running total
        # so that alignment offsets may be easily computed.
        rows = []
        curr_row = []
        row_width = 0
        row_height = 0
        curr_x = rect_left
        h_space = self._h_spacing
        for item in self._items:
            hint = item.sizeHint()
            hint_width = hint.width()
            hint_height = hint.height()
            row_item = (item, hint_width, hint_height)
            if (curr_x + hint_width) > rect_right:
                if len(curr_row) == 0:
                    rows.append((hint_width, hint_height, [row_item]))
                    row_width = 0
                    row_height = 0
                    curr_x = rect_left
                else:
                    row_width += h_space * (len(curr_row) - 1)
                    rows.append((row_width, row_height, curr_row))
                    curr_row = [row_item]
                    row_width = hint_width
                    row_height = hint_height
                    curr_x = rect_left + hint_width + h_space
            else:
                curr_row.append(row_item)
                row_width += hint_width
                row_height = max(row_height, hint_height)
                curr_x += hint_width + h_space

        # Add the final trailing row (if populated) to the list of rows.
        if len(curr_row) > 0:
            row_width += h_space * (len(curr_row) - 1)
            rows.append((row_width, row_height, curr_row))

        # If this is a test run, enough information is now available to
        # compute the layout height, and extra work can be skipped.
        if test:
            y = rect.y()
            for ignored1, row_height, ignored2 in rows:
                y += row_height
            y += self._v_spacing * (len(rows) - 1)
            return y

        # A function to compute the alignment offset given a row width.
        align = self._alignment
        if align == Qt.AlignLeading:
            align_offset = lambda w: rect_left
        elif align == Qt.AlignTrailing:
            align_offset = lambda w: max(rect_right - w, rect_left)
        else:
            align_offset = lambda w: max((rect_right - w) / 2, rect_left)

        # A function to order the row items for the layout fill.
        if self._reverse_fill:
            fill_order = lambda items: reversed(items)
        else:
            fill_order = lambda items: items

        # Loop over the rows and apply the item layout geometries.
        next_y = 0
        curr_y = rect.y()
        v_space = self._v_spacing
        for row_width, row_height, row_items in rows:
            curr_x = align_offset(row_width)
            for item, width, height in fill_order(row_items):
                r = QRect(curr_x, curr_y, width, height)
                item.setGeometry(r)
                next_y = max(next_y, curr_y + height + v_space)
                curr_x += width + h_space
            curr_y = next_y

        return curr_y

    def _doVerticalLayout(self, rect, test):
        """ Perform the layout for a vertical orientation.

        The method signature is identical to the `_doLayout` method.

        """
        rect_top = rect.y()
        rect_bottom = rect_top + rect.height()

        # This loop passes over the list of items and separates them
        # into individual rows. A given item is allowed to overflow a
        # row if it is the only member of the row. An item at the end
        # of  a populated row which overflows is moved to the next line.
        # The total width and height of a row is kept as a running total
        # so that alignment offsets may be easily computed.
        columns = []
        curr_col = []
        col_width = 0
        col_height = 0
        curr_y = rect_top
        v_space = self._v_spacing
        for item in self._items:
            hint = item.sizeHint()
            hint_width = hint.width()
            hint_height = hint.height()
            col_item = (item, hint_width, hint_height)
            if (curr_y + hint_height) > rect_bottom:
                if len(curr_col) == 0:
                    columns.append((hint_width, hint_height, [col_item]))
                    col_width = 0
                    col_height = 0
                    curr_y = rect_top
                else:
                    col_height += v_space * (len(curr_col) - 1)
                    columns.append((col_width, col_height, curr_col))
                    curr_col = [col_item]
                    col_width = hint_width
                    col_height = hint_height
                    curr_y = rect_top + hint_height + v_space
            else:
                curr_col.append(col_item)
                col_height += hint_height
                col_width = max(col_width, hint_width)
                curr_y += hint_height + v_space

        # Add the final trailing row (if populated) to the list of rows.
        if len(curr_col) > 0:
            col_height += v_space * (len(curr_col) - 1)
            columns.append((col_width, col_height, curr_col))

        # If this is a test run, enough information is now available to
        # compute the layout height, and extra work can be skipped.
        if test:
            x = rect.x()
            for col_width, ignored1, ignored2 in columns:
                x += col_width
            x += self._h_spacing * (len(columns) - 1)
            return x

        # A function to compute the alignment offset given a row width.
        align = self._alignment
        if align == Qt.AlignLeading:
            align_offset = lambda h: rect_top
        elif align == Qt.AlignTrailing:
            align_offset = lambda h: max(rect_bottom - h, rect_top)
        else:
            align_offset = lambda h: max((rect_bottom - h) / 2, rect_top)

        # A function to order the row items for the layout fill.
        if self._reverse_fill:
            fill_order = lambda items: reversed(items)
        else:
            fill_order = lambda items: items

        # Loop over the rows and apply the item layout geometries.
        next_x = 0
        curr_x = rect.x()
        h_space = self._h_spacing
        for col_width, col_height, col_items in columns:
            curr_y = align_offset(col_height)
            for item, width, height in fill_order(col_items):
                r = QRect(curr_x, curr_y, width, height)
                item.setGeometry(r)
                next_x = max(next_x, curr_x + width + h_space)
                curr_y += height + v_space
            curr_x = next_x

        return curr_x


class QFlowArea(QScrollArea):

    def __init__(self, *args, **kwargs):
        super(QFlowArea, self).__init__(*args, **kwargs)
        self.setWidgetResizable(True)
        self._area_widget = QFrame(self)
        self._area_layout = QFlowLayout()
        self._area_widget.setLayout(self._area_layout)
        self.setWidget(self._area_widget)

    def addWidget(self, widget):
        self._area_layout.addWidget(widget)

    def insertWidget(self, index, widget):
        self._area_layout.insertWidget(index, widget)

    def margins(self):
        return self._area_layout.getContentsMargins()

    def setMargins(self, left, top, right, bottom):
        self._area_layout.setContentsMargins(left, top, right, bottom)

    def aligment(self):
        return self._area_layout.alignment()

    def setAlignment(self, alignment):
        self._area_layout.setAlignment(alignment)

    def orientation(self):
        return self._area_layout.orientation()

    def setOrientation(self, orientation):
        self._area_layout.setOrientation(orientation)

    def reverseFill(self):
        return self._area_layout.reverseFill()

    def setReverseFill(self, enable):
        self._area_layout.setReverseFill(enable)

    def verticalSpacing(self):
        return self._area_layout.verticalSpacing()

    def setVerticalSpacing(self, spacing):
        self._area_layout.setVerticalSpacing(spacing)

    def horizontalSpacing(self):
        return self._area_layout.horizontalSpacing()

    def setHorizontalSpacing(self, spacing):
        self._area_layout.setHorizontalSpacing(spacing)


class QtFlowArea(QtConstraintsWidget):
    """ A Qt implementation of an Enaml FlowArea.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying widget.

        """
        return QFlowArea(parent)

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(QtFlowArea, self).create(tree)
        self.set_align(tree['align'])
        self.set_orientation(tree['orientation'])
        self.set_reverse_fill(tree['reverse_fill'])
        self.set_horizontal_spacing(tree['horizontal_spacing'])
        self.set_vertical_spacing(tree['vertical_spacing'])
        self.set_margins(tree['margins'])

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtFlowArea, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, QtFlowItem):
                widget.addWidget(child.widget())

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtMdiArea.

        """
        # if isinstance(child, QtMdiWindow):
        #     self.widget().removeSubWindow(child.widget())

    def child_added(self, child):
        """ Handle the child added event for a QtMdiArea.

        """
        # The size hint of a QMdiArea is typically quite large and the
        # size hint constraints are usually ignored. There is no need
        # to notify of a change in size hint here.
        # if isinstance(child, QtMdiWindow):
        #     self.widget().addSubWindow(child.widget())

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_align(self, content):
        """ Handle the 'set_align' action from the Enaml widget.

        """
        self.set_align(content['align'])

    def on_action_set_orientation(self, content):
        """ Handle the 'set_orientation' action from the Enaml widget.

        """
        self.set_orientation(content['orientation'])

    def on_action_set_reverse_fill(self, content):
        """ Handle the 'set_reverse_fill' action from the Enaml widget.

        """
        self.set_reverse_fill(content['reverse_fill'])

    def on_action_set_horizontal_spacing(self, content):
        """ Handle the 'set_horizontal_spacing' action from the Enaml
        widget.

        """
        self.set_horizontal_spacing(content['horizontal_spacing'])

    def on_action_set_vertical_spacing(self, content):
        """ Handle the 'set_vertical_spacing' action from the Enaml
        widget.

        """
        self.set_vertical_spacing(content['vertical_spacing'])

    def on_action_set_margins(self, content):
        """ Handle the 'set_margins' action from the Enaml widget.

        """
        self.set_margins(content['margins'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_align(self, align):
        """ Set the alignment for the underlying control.

        """
        self.widget().setAlignment(_ALIGN_MAP[align])

    def set_orientation(self, orientation):
        """ Set the orientation for the underlying control.

        """
        self.widget().setOrientation(_ORIENTATION_MAP[orientation])

    def set_reverse_fill(self, enable):
        """ Set the reverse fill property for the underlying control.

        """
        self.widget().setReverseFill(enable)

    def set_horizontal_spacing(self, spacing):
        """ Set the horizontal spacing of the underyling control.

        """
        self.widget().setHorizontalSpacing(spacing)

    def set_vertical_spacing(self, spacing):
        """ Set the vertical spacing of the underlying control.

        """
        self.widget().setVerticalSpacing(spacing)

    def set_margins(self, margins):
        """ Set the margins of the underlying control.

        """
        top, right, bottom, left = margins
        self.widget().setMargins(left, top, right, bottom)

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def replace_constraints(self, old_cns, new_cns):
        """ A reimplemented QtConstraintsWidget layout method.

        Constraints layout may not cross the boundary of a ScrollArea,
        so this method is no-op which stops the layout propagation.

        """
        pass

