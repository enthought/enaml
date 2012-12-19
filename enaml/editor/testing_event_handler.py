from enaml.qt.qt.QtCore import Qt

from .event_handler import EventHandler


class TestingEventHandler(EventHandler):

    def mouse_pressed(self, editor, event):
        cursor = editor.cursor()
        if cursor is not None:
            x = event.y()
            y = event.y()
            lineno = editor.map_to_line(y)
            position = (x - 4) / editor._char_width
            cursor.move(lineno, position)
            return True
        return False

    def key_pressed(self, editor, event):
        cursor = editor.cursor()
        if cursor is not None:
            k = event.key()
            if k == Qt.Key_Down:
                cursor.move_down()
            elif k == Qt.Key_Up:
                cursor.move_up()
            elif k == Qt.Key_Left:
                cursor.move_left()
            elif k == Qt.Key_Right:
                cursor.move_right()
            else:
                return False
            return True
        return False

