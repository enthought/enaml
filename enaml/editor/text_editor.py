import sys

from enaml.qt.qt.QtCore import Qt, QMargins, QPoint, QRect, QSize, QTimer
from enaml.qt.qt.QtGui import QAbstractScrollArea, QPainter, QFont

from .document import Document
from .event_handler import EventHandler


# Qt::WA_StaticContents is broken on OSX. QWidget::scroll also appears
# to not work entirely correctly and overdraws part of the buffer. On
# that platform, the whole widget must be fully repainted on scroll.
# According to the Qt bug tracker, this was fixed in version 4.8
# I've yet to test it on that version though...
if sys.platform == 'darwin':
    scrollWidget = lambda widget, dx, dy: widget.update()
else:
    scrollWidget = lambda widget, dx, dy: widget.scroll(dx, dy)


class QTextEditor(QAbstractScrollArea):
    """ A class which renders a Document into a scrollable area.

    """
    def __init__(self, parent=None):
        super(QTextEditor, self).__init__(parent)
        self._document = Document()
        self._event_handler = EventHandler()
        self._cursors = []
        self._scroll_offset = 0
        self._text_margins = QMargins(10, 0, 0, 0)

        self._key_down = False
        self._draw_cursors = True
        self._blinker = QTimer()
        self._blinker.timeout.connect(self._onBlinkCursors)
        self._blinker.setInterval(500)
        self._blinker.start()

        f = QFont('monaco', 14)
        f.setFixedPitch(True)
        self.setFont(f)
        viewport = self.viewport()
        viewport.setCursor(Qt.IBeamCursor)
        viewport.setFocusPolicy(Qt.ClickFocus)
        viewport.setAttribute(Qt.WA_StaticContents, True)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def document(self):
        """ Get the document being edited by this editor.

        Returns
        -------
        result : Document
            The document being edited by this editor.

        """
        return self._document

    def setDocument(self, document):
        """ Set the document to edit with this editor.

        Parameters
        ----------
        document : Document or None
            The document to edit with this editor. If None, the current
            document will be removed and a new empty document will be
            initialized.

        """
        old = self._document
        if document is None:
            document = Document()
        self._document = document
        self._scroll_offset = 0
        old.modified.disconnect(self._on_document_modified)
        document.modified.connect(self._on_document_modified)
        self._updateScrollbars()
        self.update()

    def eventHandler(self):
        """ Get the event handler in use by this editor.

        """
        return self._event_handler

    def setEventHandler(self, handler):
        """ Set the event handler for use by this editor.

        """
        self._event_handler = handler

    def cursors(self):
        """

        """
        return self._cursors

    def addCursor(self, cursor):
        """

        """
        self._cursors.append(cursor)
        cursor.moved.connect(self._on_cursor_moved)
        self.update()

    def textMargins(self):
        """ Get the text margins for the editor.

        """
        return self._text_margins

    def setTextMargins(self, left, top, right, bottom):
        """ Set the text margins for the editor.

        """
        self._text_margins = QMargins(left, top, right, bottom)
        self._updateScrollbars()
        self.update()

    def mapToScreen(self, position, clip=True, metrics=None):
        """ Map a document position to screen space.

        Parameters
        ----------
        position : Position
            The document postion to map to screen space.

        clip : bool, optional
            Whether or not to clip the position to the text bounds of
            the document. If False, virtual space characters will be
            added to pad the lines as needed. The default is True.

        metrics : QFontMetrics, optional
            The font metrics to use for measurement. If not provided,
            the current widget font metrics are used.

        Returns
        -------
        result : QPoint
            The screenspace point for the given position.

        """
        doc = self._document
        scroll = self._scroll_offset
        margins = self._text_margins
        lineno = position.lineno
        column = position.column
        if clip:
            lineno = max(0, min(lineno, len(doc) - 1))
            line = doc[lineno]
            column = max(0, min(column, len(line)))
        else:
            if lineno >= 0 and lineno < len(doc):
                line = doc[lineno]
            else:
                line = u''
            if len(line) < column:
                line += u' ' * (column - len(line))
        metrics = metrics or self.fontMetrics()
        x = metrics.width(line, column) + margins.left()
        y = lineno * metrics.lineSpacing() - scroll + margins.top()
        return QPoint(x, y)

    def mapToPosition(self, point, clip=True, metrics=None):
        """ Map a screen space point to a document position.

        Parameters
        ----------
        point : QPoint
            The screen space point to map to a document position.

        clip : bool, optional
            Whether or not to clip the position to the text bounds of
            the document. If False, virtual space characters will be
            added to pad the lines as needed. The default is True.

        metrics : QFontMetrics, optional
            The font metrics to use for measurement. If not provided,
            the current widget font metrics are used.

        Returns
        -------
        result : Position
            The document position nearest the screenspace point.

        """
        doc = self._document
        scroll = self._scroll_offset
        margins = self._text_margins
        metrics = metrics or self.fontMetrics()
        y = point.y()
        lineno = (y + scroll - margins.top()) / metrics.lineSpacing()
        if clip:
            lineno = max(0, min(lineno, len(doc) - 1))

    def map_screen_to_lineno(self, y, metrics=None):
        """ Map a y-coordinate in screen space to a lineno.

        Parameters
        ----------
        y : int
            The y-coordinate in screen space.

        metrics : QFontMetrics, optional
            The font metrics to use for measurement. If not provided,
            the current widget font metrics are used.

        Returns
        -------
        result : int
            The lineno of the line enclosing the given y-coordinate.
            This value may exceed the number of lines in the current
            text model.

        """
        metrics = metrics or self.fontMetrics()
        return (self._scroll_offset + y) / metrics.lineSpacing()

    def map_lineno_to_screen(self, lineno, metrics=None):
        """ Convert a line number in a screen space y-coordinate.

        Parameters
        ----------
        lineno : int
            The line number to convert to screen space. This must be
            greater than or equal to zero.

        metrics : QFontMetrics, optional
            The font metrics to use for measurement. If not provided,
            the current widget font metrics are used.

        Returns
        -------
        result : int
            The y-coordinate of the line number in screen space. This
            value may be positive or negative and will not necessarily
            lie within the current visible bounds.

        """
        metrics = metrics or self.fontMetrics()
        return lineno * metrics.lineSpacing() - self._scroll_offset

    def map_screen_to_position(self, x, line=u'', metrics=None):
        """ Map a screen x-coordinate to a character position.

        Parameters
        ----------
        x : int
            The x-coordinate in screen space. This will be adjusted for
            any current character offset.

        line : unicode, optional
            The line of text to use for determining position. If given,
            the returned value will be exact and will never exceed the
            length of the line. If not given, the return value will be
            an approximation.

        metrics : QFontMetrics, optional
            The font metrics to use for measurement. If not provided,
            the current widget font metrics are used.

        Returns
        -------
        result : int
            The position of the character closest to the x-coordinate.

        """
        x -= self._text_margins.left()
        metrics = metrics or self.fontMetrics()
        idx = x / metrics.averageCharWidth()
        if not line:
            return idx
        idx = min(idx, len(line))
        diff = metrics.width(line, idx) - x
        if diff == 0:
            return idx
        if diff > 0:
            next_idx = idx - 1
        else:
            next_idx = idx + 1
        new_diff = metrics.width(line, next_idx) - x
        while abs(new_diff) < abs(diff):
            diff = new_diff
            idx = next_idx
            if diff == 0:
                return idx
            if diff > 0:
                next_idx = idx - 1
            else:
                next_idx = idx + 1
            new_diff = metrics.width(line, next_idx) - x
        return idx

    def map_position_to_screen(self, position, line=u'', metrics=None):
        """ Map a character position to a screen x-coordinate.

        Parameters
        ----------
        position : int
            The character position in the line. This must be greater
            than or equal to zero.

        line : unicode, optional
            The line of text to use for determining position. If given,
            the returned value will be exact and will never exceed the
            length of the line. If not given, the return value will be
            an approximation.

        metrics : QFontMetrics, optional
            The font metrics to use for measurement. If not provided,
            the current widget font metrics are used.

        Returns
        -------
        result : int
            The x-coordinate of the character position. This value will
            be adjusted for any current character offset.

        """
        metrics = metrics or self.fontMetrics()
        offset = self._text_margins.left()
        if not line:
            return position * metrics.averageCharWidth() + offset
        position = min(position, len(line))
        return metrics.width(line, position) + offset

    def hit_test(self, x, y, metrics=None):
        """ Get a line number and position for an x, y coordinate pair.

        Parameters
        ----------
        x : int
            The x-coordinate to hit test.

        y : int
            The y-coordinate to hit test.

        metrics : QFontMetrics, optional
            The font metrics to use for measurement. If not provided,
            the current widget font metrics are used.

        Returns
        -------
        result : tuple
            A 2-tuple of (lineno, pos) which is the closest character
            to the given coordinate pair. If a line exists for the
            coordinate, the result will be exact. Otherwise, it will
            be an approximation.

        """
        metrics = metrics or self.fontMetrics()
        lineno = self.map_screen_to_lineno(y, metrics)
        doc = self._document
        if doc is None or lineno >= len(doc):
            line = u''
        else:
            line = doc[lineno]
        position = self.map_screen_to_position(x, line, metrics)
        return (lineno, position)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _updateScrollbars(self):
        doc = self._document
        vbar = self.verticalScrollBar()
        vbar.setMinimum(0)
        height = self.viewport().height()
        spacing = self.fontMetrics().lineSpacing()
        maximum = max(0, spacing * len(doc) - height)
        vbar.setPageStep(height)
        vbar.setSingleStep(spacing)
        vbar.setMaximum(maximum)

    def _onBlinkCursors(self):
        self._draw_cursors = not self._draw_cursors
        if self.hasFocus():
            viewport = self.viewport()
            height = viewport.height()
            width = viewport.width()
            metrics = self.fontMetrics()
            size = QSize(1, metrics.lineSpacing())
            for cursor in self._cursors:
                point = self.mapToScreen(cursor.position, False, metrics)
                y = point.y()
                x = point.x()
                if y >= 0 and y < height and x >= 0 and x < width:
                    viewport.update(QRect(point, size))

    # def _redraw_line(self, lineno, position):
    #     viewport = self.viewport()
    #     height = viewport.height()
    #     metrics = self.fontMetrics()
    #     y = self.map_lineno_to_screen(lineno, metrics)
    #     if y >= 0 and y < height:
    #         line = self._text.line(lineno)
    #         width = viewport.width()
    #         x = self.map_position_to_screen(position, line)
    #         if x >= 0 and x < width:
    #             r = QRect(x, y, width - x, metrics.lineSpacing())
    #             viewport.update(r)

    # def _redraw_lines(self, lineno):
    #     viewport = self.viewport()
    #     height = viewport.height()
    #     metrics = self.fontMetrics()
    #     y = self.map_lineno_to_screen(lineno, metrics)
    #     if y >= 0 and y < height:
    #         r = QRect(0, y, viewport.width(), height - y)
    #         viewport.update(r)

    def _on_document_modified(self, mod):
        #span = mod.invalidated_span()
        self.update()

    def _on_cursor_moved(self, old, new):
        #self._draw_caret = True

        viewport = self.viewport()
        height = viewport.height()
        width = viewport.width()
        metrics = self.fontMetrics()
        spacing = metrics.lineSpacing()

        doc = self._document

        old_lineno = old.lineno
        old_pos = old.column

        old_y = self.map_lineno_to_screen(old_lineno, metrics)
        if old_y >= 0 and old_y < height:
            if old_lineno < len(doc):
                old_line = doc[old_lineno]
                old_x = self.map_position_to_screen(old_pos, old_line, metrics)
                if old_x >= 0 and old_x < width:
                    r1 = QRect(old_x, old_y, 1, spacing)
                    viewport.update(r1)

        new_lineno = new.lineno
        new_pos = new.column

        new_y = self.map_lineno_to_screen(new_lineno, metrics)
        if new_y >= 0 and new_y < height:
            new_line = doc[new_lineno]
            new_x = self.map_position_to_screen(new_pos, new_line, metrics)
            if new_x >= 0 and new_x < width:
                r2 = QRect(new_x, new_y, 1, spacing)
                viewport.update(r2)

    #--------------------------------------------------------------------------
    # Event Handling
    #--------------------------------------------------------------------------
    def mousePressEvent(self, event):
        handler = self._event_handler
        if handler is not None:
            return handler.mouse_pressed(self, event)
        return False

    def mouseReleaseEvent(self, event):
        handler = self._event_handler
        if handler is not None:
            return handler.mouse_released(self, event)
        return False

    def mouseMoveEvent(self, event):
        handler = self._event_handler
        if handler is not None:
            return handler.mouse_moved(self, event)
        return False

    def keyPressEvent(self, event):
        self._key_down = True
        handler = self._event_handler
        if handler is not None:
            return handler.key_pressed(self, event)
        return False

    def keyReleaseEvent(self, event):
        self._key_down = False
        handler = self._event_handler
        if handler is not None:
            return handler.key_released(self, event)
        return False

    def scrollContentsBy(self, dx, dy):
        if self._document is not None:
            old = self._scroll_offset
            new = max(0, old - dy)
            if old != new:
                self._scroll_offset = new
                dy = old - new
                scrollWidget(self.viewport(), dx, dy)

    def resizeEvent(self, event):
        self._updateScrollbars()

    def paintEvent(self, event):
        """

        """
        doc = self._document
        if doc is None:
            return

        painter = QPainter(self.viewport())

        # The baseline offset is computed by evenly distributing any
        # font leading on the top and bottom of the line spacing. Odd
        # numbered leading is rounded up. The half-leading plus the font
        # ascent will yield the baseline offset. However, the value Qt
        # gives for font ascent includes one pixel for the baseline.
        # That pixel is adjusted out.
        metrics = painter.fontMetrics()
        vspace = (metrics.leading() + 1) / 2
        baseline_offset = vspace + metrics.ascent() - 1

        # Pre-fetch some commonly used values
        line_spacing = metrics.lineSpacing()
        scroll_offset = self._scroll_offset
        char_offset = self._text_margins.left()
        count = len(doc)
        cursors = self._cursors
        draw_cursors = cursors and (self._draw_cursors or self._key_down)

        # For each invalid rect in the region, all lines which vertically
        # overlap the rect are drawn. Fully drawing partial lines ensures
        # that font kerning an antialising is computed properly. Qt sets
        # the painter clip to the invalid region automatically, so that
        # work does not need to be repeated. Common mapping functions are
        # copied inline for performance reasons.
        #print event.region().rects()
        #import time
        #t1 = time.time()
        for rect in event.region().rects():
            # Inline `map_screen_to_lineno`
            lineno = (scroll_offset + rect.y()) / line_spacing
            # inline `map_lineno_to_screen`
            start_y = lineno * line_spacing - scroll_offset
            end_y = rect.bottom() + line_spacing
            curr_y = start_y
            while curr_y < end_y and lineno < count:
                line = doc[lineno]
                painter.drawText(char_offset, curr_y + baseline_offset, line)
                curr_y += line_spacing
                lineno += 1
                if lineno == count:
                    r = QRect(rect.x(), curr_y, rect.width(), end_y)
                    painter.fillRect(r, Qt.gray)
                    break


            # Draw any visible carets for this rect.
            if draw_cursors:
                for cursor in cursors:
                    cursor_lineno = cursor.position.lineno
                    line = doc[cursor_lineno]
                    # inline `map_lineno_to_screen`
                    cursor_y = cursor_lineno * line_spacing - scroll_offset
                    if cursor_y >= start_y and cursor_y <= end_y:
                        # inline `map_position_to_screen`
                        x = metrics.width(line, cursor.position.column) + char_offset
                        start = QPoint(x, cursor_y)
                        end = QPoint(x, cursor_y + line_spacing - 1)
                        painter.drawLine(start, end)
        #print time.time() - t1

