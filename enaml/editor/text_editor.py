#--------------------------------------------------|---------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

from enaml.qt.qt.QtCore import Qt, QPoint, QRect, QTimer
from enaml.qt.qt.QtGui import QAbstractScrollArea, QPainter, QFont


# Qt::WA_StaticContents is broken on OSX. QWidget::scroll also appears
# to not work entirely correctly and overdraws part of the buffer. On
# that platform, the whole widget must be fully repainted on scroll.
if sys.platform == 'darwin':
    scrollWidget = lambda widget, dx, dy: widget.update()
else:
    scrollWidget = lambda widget, dx, dy: widget.scroll(dx, dy)


class QTextEditor(QAbstractScrollArea):
    """

    """
    def __init__(self, parent=None):
        super(QTextEditor, self).__init__(parent)
        f = QFont('inconsolata-dz', 14)
        #f = QFont('consolas', 14)
        #f.setFixedPitch(True)
        #f.setKerning(False)
        self.setFont(f)
        self._text = None
        self._cursor = None
        self._event_handler = None
        self._scroll_offset = 0
        self._update_scrollbars()
        self._draw_caret = True
        self._key_down = False
        self._blink = QTimer()
        self._blink.timeout.connect(self._on_blink_caret)
        self._blink.setInterval(500)
        self._blink.start()
        self.viewport().setCursor(Qt.IBeamCursor)
        self.viewport().setFocusPolicy(Qt.ClickFocus)
        self.viewport().setAttribute(Qt.WA_StaticContents, True)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def textInterface(self):
        """ Get the text interface in use by this editor.

        """
        return self._text

    def setTextInterface(self, text):
        """ Set the text interface in use by this editor.

        """
        self._text = text
        self._scroll_offset = 0
        self._update_scrollbars()
        self.update()

    def cursor(self):
        """ Get the cursor in use by this editor.

        """
        return self._cursor

    def setCursor(self, cursor):
        """ Set the cursor for use by this editor.

        """
        self._cursor = cursor
        for caret in cursor.carets():
            self._on_caret_added(caret)
        self.update()

    def eventHandler(self):
        """ Get the event handler in use by this editor.

        """
        return self._event_handler

    def setEventHandler(self, handler):
        """ Set the event handler for use by this editor.

        """
        self._event_handler = handler

    def map_to_line(self, y, metrics=None):
        """ Convert screen space into text space.

        """
        metrics = metrics or self.fontMetrics()
        return (self._scroll_offset + y) / metrics.lineSpacing()

    def map_to_screen(self, lineno, metrics=None):
        """ Convert text space into screen space.

        """
        metrics = metrics or self.fontMetrics()
        return lineno * metrics.lineSpacing() - self._scroll_offset

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _update_scrollbars(self):
        vbar = self.verticalScrollBar()
        text = self._text
        if text is None:
            vbar.setPageStep(0)
            vbar.setSingleStep(0)
            vbar.setMaximum(0)
        else:
            height = self.viewport().height()
            vbar.setPageStep(height)
            spacing = self.fontMetrics().lineSpacing()
            vbar.setSingleStep(spacing)
            vbar.setMaximum(spacing * text.line_count() - height * 3 / 4)

    def _on_caret_added(self, caret):
        caret.moved.connect(self._on_caret_moved)

    def _on_caret_removed(self, caret):
        caret.moved.disconnect(self._on_caret_moved)

    def _on_caret_moved(self, old, new):
        self._draw_caret = True
        metrics = self.fontMetrics()
        old_y = self.map_to_screen(old[0], metrics)
        width = self.viewport().width()
        height = metrics.lineSpacing()
        r = QRect(0, old_y, width, height)
        self.update(r)
        new_y = self.map_to_screen(new[0], metrics)
        r = QRect(0, new_y, width, height)
        self.update(r)

    def _on_blink_caret(self):
        self._draw_caret = not self._draw_caret
        cursor = self._cursor
        if cursor is not None and self.hasFocus():
            #width = self.viewport().width()
            height = self.fontMetrics().lineSpacing()
            for caret in cursor.carets():
                y = self.map_to_screen(caret.lineno)
                line = self._text.line(caret.lineno)
                m = self.fontMetrics()
                w = m.width(line[:caret.position])
                r = QRect(w + 5, y, 1, height)
                self.viewport().update(r)

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
        if self._text is not None:
            self._scroll_offset -= dy
            scrollWidget(self.viewport(), dx, dy)

    def resizeEvent(self, event):
        self._update_scrollbars()

    def paintEvent(self, event):
        text = self._text
        if text is None:
            return

        import time
        t1 = time.time()
        painter = QPainter(self.viewport())
        metrics = painter.fontMetrics()

        height = metrics.height()
        spacing = metrics.lineSpacing()
        offset = self._scroll_offset
        d = (spacing - height) / 2
        ds = metrics.descent()
        baseline_ofs = spacing - d - ds

        draw_caret = self._draw_caret or self._key_down
        count = text.line_count()
        for rect in event.region().rects():
            # inline `map_to_lineno`
            lineno = (rect.y() + offset) / spacing
            # inline `map_to_screen`
            y = start_y = lineno * spacing - offset
            end_y = rect.bottom() + spacing
            while y < end_y and lineno < count:
                line = text.line(lineno)
                #painter.save()
                #painter.setPen(Qt.blue)
                #painter.drawLine(QPoint(0, y), QPoint(rect.width(), y))
                # painter.setPen(Qt.red)
                # painter.drawLine(QPoint(0, y + baseline_ofs), QPoint(rect.width(), y + baseline_ofs))
                #painter.setPen(Qt.green)
                #painter.drawLine(QPoint(0, y + spacing - 1), QPoint(rect.width(), y + spacing - 1))
                # painter.setPen(Qt.darkYellow)
                # painter.drawLine(QPoint(0, y + spacing - 1 - d), QPoint(rect.width(), y + spacing - d - 1))
                #painter.restore()
                painter.drawText(5, y + baseline_ofs, line)

                lineno += 1
                y += spacing

            # draw the carets
            cursor = self._cursor
            if cursor is not None and draw_caret:
                for caret in cursor.carets():
                    caret_lineno = caret.lineno
                    line = text.line(caret_lineno)
                    ct = caret_lineno * spacing - offset
                    if ct >= start_y and ct <= end_y:
                        w = metrics.width(line[:caret.position], -1, 0)
                        x = w + 5
                        painter.drawLine(QPoint(x, ct), QPoint(x, ct + spacing - 1))
        print time.time() - t1
