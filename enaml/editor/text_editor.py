#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from PySide.QtGui import QAbstractScrollArea, QPainter, QPalette
from PySide.QtCore import Qt, QPoint

from .text_cursor import TextCursor


class TextEditor(QAbstractScrollArea):

    def __init__(self, document):
        super(TextEditor, self).__init__()
        self.document = document
        self.v_offset = 0
        self.v_height = 0
        self.line_height = 0
        self.init_metrics()
        self.viewport().setAttribute(Qt.WA_StaticContents, True)
        self.cursor = TextCursor(document)
        self.viewport().setCursor(Qt.IBeamCursor)
        self.viewport().setFocusPolicy(Qt.ClickFocus)
        p = self.viewport().palette()
        p.setColor(QPalette.Base, Qt.black)
        self.viewport().setPalette(p)

    def init_metrics(self):
        self.line_height = self.fontMetrics().height()
        self.line_spacing = self.fontMetrics().lineSpacing()
        self.v_height = self.document.line_count() * self.line_height
        self.verticalScrollBar().setMaximum(self.v_height - 150)

    def mousePressEvent(self, event):
        y = event.y()
        w = self.fontMetrics().averageCharWidth()
        pos = event.x() / w
        lineno = self.hit_test(y)
        self.cursor.move_abs(lineno, pos)
        self.viewport().update()

    def keyPressEvent(self, event):
        k = event.key()
        if k == Qt.Key_Down:
            self.cursor.move_down()
            self.viewport().update()
            return True
        if k == Qt.Key_Up:
            self.cursor.move_up()
            self.viewport().update()
            return True
        if k == Qt.Key_Left:
            self.cursor.move_left()
            self.viewport().update()
            return True
        if k == Qt.Key_Right:
            self.cursor.move_right()
            self.viewport().update()
            return True
        if k == Qt.Key_Backspace:
            self.cursor.backspace()
            self.viewport().update()
            return True
        if k == Qt.Key_Return:
            self.cursor.newline()
            self.viewport().update()
            return True
        if k == Qt.Key_Tab:
            self.cursor.insert(u' ' * 4)
            self.viewport().update()
            return True
        t = event.text()
        if t:
            self.cursor.insert(t)
            self.viewport().update()
            return True
        return False

    def scrollContentsBy(self, dx, dy):
        self.v_offset -= dy
        self.viewport().scroll(0, dy)

    def resizeEvent(self, event):
        height = self.viewport().height()
        self.verticalScrollBar().setMaximum(self.v_height - height * 3 / 4)
        self.verticalScrollBar().setPageStep(height)
        self.verticalScrollBar().setSingleStep(self.line_height)

    def hit_test(self, y):
        v_y = self.v_offset + y
        return self.document.line_count() * v_y / self.v_height

    def line_top(self, lineno):
        return lineno * self.line_height

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        rect = event.rect()
        lineno = self.hit_test(rect.y())
        v_top = self.line_top(lineno)
        y = start_y = v_top - self.v_offset
        yf = rect.y() + rect.height() + self.line_height

        painter.setPen(Qt.white)
        document = self.document
        n = self.document.line_count()
        lh = self.line_spacing
        yo = self.fontMetrics().descent()
        while y < yf and lineno < n:
            line = document.line(lineno)
            painter.drawText(5, y + lh - yo, line)
            lineno += 1
            y += lh

        # draw the cursor
        clineno = self.cursor.lineno()
        ct = self.line_top(clineno) - self.v_offset
        if ct >= start_y and ct <= yf:
            x = self.cursor.position() * self.fontMetrics().averageCharWidth()
            x += 4
            painter.drawLine(QPoint(x, ct), QPoint(x, ct + lh))

