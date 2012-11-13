#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import QSize
from .qt.QtGui import QLayout, QWidgetItem


class QSingleWidgetItem(QWidgetItem):
    """ A QWidgetItem subclass for use with the QSingleWidgetLayout.

    The semantics of this widget item are slightly different from that
    of the standard QWidgetItem; it always aligns its widget with the
    top left of the layout rect. This class is expressly meant for use
    by the QSingleWidgetLayout.

    """
    def setGeometry(self, rect):
        """ Set the rectangle covered by this layout item.

        Parameters
        ----------
        rect : QRect
            The rectangle that this layout item should cover.

        """
        if self.isEmpty():
            return
        s = rect.size().boundedTo(self.maximumSize())
        self.widget().setGeometry(rect.x(), rect.y(), s.width(), s.height())


class QSingleWidgetLayout(QLayout):
    """ A QLayout subclass which can have at most one layout item.

    The layout item is expanded to fit the allowable space; similar to
    how a central widget behaves in a QMainWindow. Unlike QMainWindow,
    this layout respects the maximum size of the widget. The default
    contents margins of this layout is 0px in all directions.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a QSingleWidgetLayout.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a QLayout.

        """
        super(QSingleWidgetLayout, self).__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)
        self._item = None

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def widget(self):
        """ Get the widget being managed by this layout.

        Returns
        -------
        result : QWidget or None
            The widget being managed by this layout or None if it does
            not exist.

        """
        item = self._item
        if item is not None:
            return item.widget()

    def setWidget(self, widget):
        """ Set the widget for this layout.

        Parameters
        ----------
        widget : QWidget
            The widget to manage with this layout.

        """
        self.takeAt(0)
        if widget is not None:
            self.addChildWidget(widget)
            self.addItem(QSingleWidgetItem(widget))
            widget.setVisible(True)
            self.update()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def addWidget(self, widget):
        """ Overridden parent class method. This method redirects to the
        `setWidget` method. User code should call `setWidget` instead.

        """
        import warnings
        msg = ('`QSingleWidgetLayout.addWidget`: use the '
               '`QSingleWidgetLayout.setWidget` method instead.')
        warnings.warn(msg)
        self.setWidget(widget)

    def addItem(self, item):
        """ A virtual method implementation which sets the layout item
        in the layout. The old item will be overridden.

        """
        self._item = item

    def count(self):
        """ A virtual method implementation which returns 0 if no layout
        item is supplied, or 1 if there is a current layout item.

        """
        return 0 if self._item is None else 1

    def itemAt(self, idx):
        """ A virtual method implementation which returns the layout item
        for the given index or None if one does not exist.

        """
        if idx == 0:
            return self._item

    def takeAt(self, idx):
        """ A virtual method implementation which removes and returns the
        item at the given index or None if one does not exist.

        """
        if idx == 0:
            res = self._item
            self._item = None
            if res is not None:
                old = res.widget()
                if old is not None:
                    old.hide()
            return res

    def sizeHint(self):
        """ A virtual method implementation which returns the size hint
        for the layout.

        """
        item = self._item
        if item is not None:
            hint = item.sizeHint()
            left, top, right, bottom = self.getContentsMargins()
            hint.setHeight(hint.height() + top + bottom)
            hint.setWidth(hint.width() + left + right)
            return hint
        return QSize()

    def setGeometry(self, rect):
        """ A reimplemented method which sets the geometry of the managed
        widget to fill the given rect.

        """
        super(QSingleWidgetLayout, self).setGeometry(rect)
        item = self._item
        if item is not None:
            item.setGeometry(self.contentsRect())

    def minimumSize(self):
        """ A reimplemented method which returns the minimum size hint
        of the layout item widget as the minimum size of the window.

        """
        item = self._item
        if item is not None:
            s = item.minimumSize()
            left, top, right, bottom = self.getContentsMargins()
            s.setHeight(s.height() + top + bottom)
            s.setWidth(s.width() + left + right)
            return s
        return super(QSingleWidgetLayout, self).minimumSize()

    def maximumSize(self):
        """ A reimplemented method which returns the maximum size hint
        of the layout item widget as the maximum size of the window.

        """
        item = self._item
        if item is not None:
            s = item.maximumSize()
            left, top, right, bottom = self.getContentsMargins()
            s.setHeight(s.height() + top + bottom)
            s.setWidth(s.width() + left + right)
            return s
        return super(QSingleWidgetLayout, self).maximumSize()

