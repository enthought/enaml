from enaml.qt.qt.QtCore import Qt

from .event_handler import EventHandler
from .indexing import Position


class TestingEventHandler(EventHandler):

    def mouse_pressed(self, editor, event):
        cursors = editor.cursors()
        if cursors:
            for cursor in cursors:
                x = event.x()
                y = event.y()
                lineno, position = editor.hit_test(x, y)
                cursor.move(Position(lineno, position))
            return True
        return False

    def key_pressed(self, editor, event):
        cursors = editor.cursors()
        if cursors:
            k = event.key()
            if k == Qt.Key_Down:
                for cursor in cursors:
                    cursor.move_down()
            elif k == Qt.Key_Up:
                for cursor in cursors:
                    cursor.move_up()
            elif k == Qt.Key_Left:
                for cursor in cursors:
                    cursor.move_left()
            elif k == Qt.Key_Right:
                for cursor in cursors:
                    cursor.move_right()
            elif k == Qt.Key_Backspace:
                for cursor in cursors:
                    cursor.backspace()
            elif k == Qt.Key_Delete:
                for cursor in cursors:
                    cursor.delete()
            elif k == Qt.Key_Return:
                for cursor in cursors:
                    cursor.newline()
            elif event.text():
                for cursor in cursors:
                    cursor.insert(event.text())
            else:
                return False
            return True
        return False

