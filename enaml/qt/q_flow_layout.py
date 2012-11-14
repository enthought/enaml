#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
import time

from .qt.QtCore import Qt, QSize, QRect
from .qt.QtGui import QLayout, QWidgetItem


class AbstractFlowWidget(object):
    """ An abstract base class which defines the interface for widgets
    which can be used in a QFlowLayout.

    Users of QFlowLayout must register their custom QWidget classes with
    this class in order to use the QFlowLayout.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def layoutData(self):
        """ An abstractmethod which must be implemented by subclasses.

        Returns
        -------
        result : FlowLayoutData
            The FlowLayoutData instance to use for this widget. The
            same data layout data instance should be returned for
            each call to this method.

        """
        raise NotImplementedError


class FlowLayoutData(object):
    """ The layout data object to use with AbstractFlowWidget instances.

    For performance reasons, there are no runtime checks on the limits
    of the values assigned to this class. Users should ensure that the
    values assigned conform to the documented limits. Users must set
    the `dirty` flag to True before calling `updateGeometry` in order
    for changes to have effect.

    """
    #: Whether or not the computed info for the layout item is dirty.
    #: This must be set to True before calling `updateGeometry` on
    #: the owner widget.
    dirty = True

    #: The flow stretch factor of the layout item. This value controls
    #: the amount of space that is taken up by an expandable item in the
    #: direction of the layout flow, relative to the other items in the
    #: line. The minimum is 0 which means the item should not expand.
    #: There is no maximum.
    stretch = 0

    #: The ortho stretch factor of the layout item. This value controls
    #: the amount of space that is taken up by an expandable item in the
    #: direction orthogonal to the layout flow, relative to other items
    #: in the line. The minimum is 0 which means the item should not
    #: expand. There is no maximum.
    ortho_stretch = 0

    #: The alignment of the layout item in the direction orthogonal to
    #: the layout flow. This must be one of the enums Qt.AlignLeading,
    #: Qt.AlignTrailing, or Qt.AlignCenter.
    align = Qt.AlignLeading

    #: The preferred size for the layout item. This size will be used
    #: as the size of the layout item to the extent possible. If the
    #: given size is invalid, the sizeHint of the item will be used.
    preferred_size = QSize()

    def __init__(self):
        """ Initialize a FlowLayoutData.

        """
        self.preferred_size = QSize()


class QFlowWidgetItem(QWidgetItem):
    """ A custom QWidgetItem for use with the QFlowLayout.

    """
    def __init__(self, widget, data):
        """ Initialize a QFlowWidgetItem.

        Parameters
        ----------
        widget : QWidget
            The widget to manage with this item.

        data : FlowLayoutData
            The layout data struct associated with this item.

        """
        super(QFlowWidgetItem, self).__init__(widget)
        self.data = data
        self._cached_hint = QSize()
        self._cached_max = QSize()
        self._cached_min = QSize()

    def maximumSize(self):
        """ Overridden maximum size computation. The max size for a flow
        widget item is cached.

        """
        if not self._cached_max.isValid():
            self._cached_max = super(QFlowWidgetItem, self).maximumSize()
        return self._cached_max

    def minimumSize(self):
        """ Overridden minimum size computation. The min size for a flow
        widget item is cached.

        """
        if not self._cached_min.isValid():
            self._cached_min = super(QFlowWidgetItem, self).minimumSize()
        return self._cached_min

    def sizeHint(self):
        """ Overridden size hint computation. The size hint for a flow
        widget item is cached.

        """
        if not self._cached_hint.isValid():
            hint = self.data.preferred_size
            if hint.isValid():
                hint = hint.expandedTo(self.minimumSize())
                hint = hint.boundedTo(self.maximumSize())
            else:
                hint = super(QFlowWidgetItem, self).sizeHint()
            self._cached_hint = hint
        return self._cached_hint

    def invalidate(self):
        """ Invalidate the internal cached data for this widget item.

        Invalidation will only occur if the layout data is dirty.

        """
        if self.data.dirty:
            self._cached_hint = QSize()
            self._cached_min = QSize()
            self.data.dirty = False


class _LayoutRow(object):
    """ A private class used by QFlowLayout.

    This class accumulates information about a row of items as the items
    are added to the row. Instances of the this class are created by a
    _LayoutContainer on an as-needed basis.

    """
    def __init__(self, spacing):
        """ Initialize a layout row.

        Parameters
        ----------
        spacing : int
            The horizontal spacing to place between each item in the
            row.

        """
        self.spacing = spacing
        self.min_height = 0
        self.des_height = 0
        self.diff = 0
        self.stretch = 0
        self.width = 0
        self.height = 0
        self.items = []

    def add_item(self, item):
        """ Add an item to the layout row.

        Parameters
        ----------
        item : QFlowWidgetItem
            The flow widget item to add to the layout row.

        """
        min_size = item.minimumSize()
        hint_size = item.sizeHint()
        self.min_height = max(self.min_height, min_size.height())
        self.des_height = max(self.des_height, hint_size.height())
        self.diff = self.des_height - self.min_height
        self.stretch += item.data.stretch
        self.width += hint_size.width()
        if len(self.items) > 0:
            self.width += self.spacing
        self.items.append(item)

    def layout(self, rect_x, rect_y):
        curr_x = rect_x
        space = self.spacing
        for item in self.items:
            s = item.sizeHint()
            w = s.width()
            if item.data.stretch > 0:
                h = self.height
            else:
                h= min(s.height(), self.height)
            r = QRect(curr_x, rect_y, w, h)
            item.setGeometry(r)
            curr_x += (w + space)


class _HLayoutContainer(object):
    """ A private class used by QFlowLayout.

    This class accumulates information about a horizontal flow layout.
    Items can be added to an instance of this class and they will be
    automatically classified into rows. Unlike the _LayoutRow class,
    this class does not keep a running total of its data. The `update`
    method should be explicitly called to update the layout metrics.

    """
    def __init__(self, h_spacing, v_spacing, width):
        """ Initialize an _HLayoutContainer.

        Parameters
        ----------
        h_spacing : int
            The horizontal spacing to place between items.

        v_spacing : int
            The vertical spacing to place between rows.

        width : int
            The width of the layout area.

        """
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        self._width = width
        self._rows = []
        self._min_height = 0
        self._des_height = 0
        self._total_diff = 0
        self._total_stretch = 0

    def add_item(self, item):
        """ Add an item to the layout container.

        The item will be automatically added to the proper row.

        """
        rows = self._rows
        h_space = self._h_spacing
        if len(rows) == 0:
            row = _LayoutRow(h_space)
            row.add_item(item)
            rows.append(row)
        else:
            row = rows[-1]
            hint = item.sizeHint()
            if (row.width + h_space + hint.width()) > self._width:
                row = _LayoutRow(h_space)
                row.add_item(item)
                rows.append(row)
            else:
                row.add_item(item)

    def update(self):
        """ Update the layout metrics for the current set of rows.

        """
        space = self._v_spacing * (len(self._rows) - 1)
        min_height = space
        des_height = space
        total_diff = 0
        total_stretch = 0
        for row in self._rows:
            min_height += row.min_height
            des_height += row.des_height
            total_diff += row.diff
            total_stretch += row.stretch
        self._min_height = min_height
        self._des_height = des_height
        self._total_diff = total_diff
        self._total_stretch = total_stretch

    def size_rows(self, space):
        """ Size the row for the given amount of free space.

        This will distribute the space fairly according to the relative
        difference of rows desired height versus min height. A given row
        will not being sized larger than its desired size.

        Parameters
        ----------
        space : int
            The amount of free vertical space to distribute to rows.

        Returns
        -------
        result : int
            The sized height of the container.

        """
        height = 0
        space = max(0, space)
        total = max(self._total_diff, 1) # Guard against divide by zero
        for row in self._rows:
            d = space * row.diff / total
            row.height = min(row.min_height + d, row.des_height)
            height += row.height
        height += self._v_spacing * (len(self._rows) - 1)
        return height

    def distribute(self, space):
        """ Distribute extra space amongst the rows according to their
        stretch factors.

        Parameters
        ----------
        space : int
            The amount of free vertical space to distribute to rows.

        """
        space = max(0, space)
        total = self._total_stretch
        if space > 0 and total > 0:
            for row in self._rows:
                if row.stretch > 0:
                    d = space * row.stretch / total
                    row.height += d

    def min_height(self):
        """ Get the minimum required height for the container.

        Returns
        -------
        result : int
            The minimum height required by the container.

        """
        return self._min_height

    def height(self):
        """ Compute and return the height of the container.

        Returns
        -------
        result : int
            The total height occupied by the container.

        """
        height = 0
        for row in self._rows:
            height += row.height
        height += self._v_spacing * (len(self._rows) - 1)
        return height

    def layout(self, rect_x, rect_y):
        """ Layout the items according to the current state.

        """
        height = 0
        curr_y = rect_y
        space = self._v_spacing
        for row in self._rows:
            row.layout(rect_x, curr_y)
            d = row.height + space
            height += d
            curr_y += d
        return height


class QFlowLayout(QLayout):
    """ A custom QLayout which implements a flowing warparound layout.

    """
    def __init__(self):
        """ Initialize a QFlowLayout.

        """
        super(QFlowLayout, self).__init__()
        self._items = []
        self._alignment = Qt.AlignLeading
        self._orientation = Qt.Horizontal
        self._reverse_fill = False
        self._cached_w = -1
        self._cached_hfw = -1
        self._cached_min = None
        self._cached_hint = None
        self._v_spacing = 10
        self._h_spacing = 10
        self._wfh_size = None

    def addWidget(self, widget):
        """ Add a widget to the end of the flow layout.

        Parameters
        ----------
        widget : AbstractFlowWidget
            The flow widget to add to the layout.

        """
        self.insertWidget(self.count(), widget)

    def insertWidget(self, index, widget):
        """ Insert a widget into the flow layout.

        Parameters
        ----------
        index : int
            The index at which to insert the widget.

        widget : AbstractFlowWidget
            The flow widget to insert into the layout.

        """
        assert isinstance(widget, AbstractFlowWidget), 'invalid widget type'
        self.addChildWidget(widget)
        item = QFlowWidgetItem(widget, widget.layoutData())
        self._items.insert(index, item)
        widget.show()
        self.invalidate()

    def alignment(self):
        """ Get the edge alignment for the lines in the layout.

        Returns
        -------
        result : enum
            The edge alignment of the lines in the layout. This will be
            one of Qt.AlignLeading, Qt.AlignTrailing, or Qt.AlignCenter.
            The default is Qt.AlignLeading.

        """
        return self._alignment

    def setAlignment(self, alignment):
        """ Set the alignment for a line in the layout.

        Parameters
        ----------
        alignment : enum
            The edge alignment of the lines in the layout. This must be
            one of Qt.AlignLeading, Qt.AlignTrailing, or Qt.AlignCenter.

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
            The orientation of the layout. This will be Qt.Horizontal
            or Qt.Vertical. The default is Qt.Horizontal.

        """
        return self._orientation

    def setOrientation(self, orientation):
        """ Set the orientation of the flow layout.

        Parameters
        ----------
        orientation : enum
            The orientation of the layout. This must be Qt.Horizontal
            or Qt.Vertical.

        """
        allowed = (Qt.Horizontal, Qt.Vertical)
        assert orientation in allowed, 'invalid orientation'
        self._orientation = orientation
        self.invalidate()

    def reverseFill(self):
        """ Whether reverse fill is enabled for this layout.

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
            The number of pixels of horizontal space between items in
            the layout. The default is 10px.

        """
        return self._h_spacing

    def setHorizontalSpacing(self, spacing):
        """ Set the horizontal spacing for the layout.

        Parameters
        ----------
        spacing : int
            The number of pixels of horizontal space to place between
            items in the layout.

        """
        self._h_spacing = spacing
        self.invalidate()

    def verticalSpacing(self):
        """ Get the vertical spacing for the layout.

        Returns
        -------
        result : int
            The number of pixels of vertical space between items in the
            layout. The default is 10px.

        """
        return self._v_spacing

    def setVerticalSpacing(self, spacing):
        """ Set the vertical spacing for the layout.

        Parameters
        ----------
        spacing : int
            The number of pixels of vertical space to place between
            items in the layout.

        """
        self._v_spacing = spacing
        self.invalidate()

    def hasHeightForWidth(self):
        """ Whether the height of the layout depends on its width.

        Returns
        -------
        result : bool
            True if the orientation is horizontal, False otherwise.

        """
        return self._orientation == Qt.Horizontal

    def heightForWidth(self, width):
        """ Get the height of the layout for the given width.

        This value only applies if `hasHeightForWidth` returns True.

        Parameters
        ----------
        width : int
            The width for which to determine a height.

        """
        if self._cached_w != width:
            left, top, right, bottom = self.getContentsMargins()
            adj_width = width - (left + right)
            height = self._doLayout(QRect(0, 0, adj_width, 0), True)
            self._cached_hfw = height + top + bottom
            self._cached_w = adj_width
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
        self._cached_hint = None
        self._wfh_size = None
        for item in self._items:
            item.invalidate()
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

    def setGeometry(self, rect):
        """ Sets the geometry of all the items in the layout.

        """
        super(QFlowLayout, self).setGeometry(rect)
        self._doLayout(self.contentsRect())

    def sizeHint(self):
        """ A virtual method implementation which returns the size hint
        for the layout.

        """
        if self._cached_hint is None:
            size = QSize(0, 0)
            for item in self._items:
                size = size.expandedTo(item.sizeHint())
            left, top, right, bottom = self.getContentsMargins()
            size.setWidth(size.width() + left + right)
            size.setHeight(size.height() + top + bottom)
            self._cached_hint = size
        return self._cached_hint

    def minimumSize(self):
        """ A reimplemented method which returns the minimum size hint
        of the layout item widget as the minimum size of the window.

        """
        if self._cached_min is None:
            size = QSize(0, 0)
            for item in self._items:
                size = size.expandedTo(item.minimumSize())
            left, top, right, bottom = self.getContentsMargins()
            size.setWidth(size.width() + left + right)
            size.setHeight(size.height() + top + bottom)
            self._cached_min = size
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
        #import time
        #t1 = time.clock()
        if self._orientation == Qt.Vertical:
            res = self._doVerticalLayout(rect, test)
            # s = rect.size()
            # s.setWidth(res)
            # self._wfh_size = s
        else:
            res = self._doHorizontalLayout(rect, test)
        #t2 = time.clock()
        #print t2 - t1
        return res

    def _doHorizontalLayout(self, rect, test):
        """ Perform the layout for a horizontal orientation.

        The method signature is identical to the `_doLayout` method.

        """
        # Add the items to a layout container. The container implements
        # the majority of the distribution and layout logic.
        h_space = self._h_spacing
        v_space = self._v_spacing
        container = _HLayoutContainer(h_space, v_space, rect.width())
        for item in self._items:
            container.add_item(item)

        # Once all items added to the container and classified, the
        # container can update its internal layout metrics.
        container.update()

        # If this is a test run, the minimum layout height is all that
        # is required. No other work needs to be performed.
        if test:
            return container.min_height()

        # Distribute the extra available space. If the rect is smaller
        # than the required min, then each row gets its minimum height.
        # Otherwise, the space is distributed to the rows based on the
        # relative magnitude of their height differences.
        rect_height = rect.height()
        delta = rect_height - container.min_height()
        height = container.size_rows(delta)

        # Redistribute any remaining space to rows which can stretch.
        remaining = rect_height - height
        container.distribute(remaining)

        # XXX add layout options

        # Finally, walk the structure and layout the items.
        return container.layout(rect.x(), rect.y())

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
