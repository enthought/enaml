from enaml.qt.qt.QtGui import QApplication

from enaml.editor.text_editor import QTextEditor
from enaml.editor.cursor import Cursor
from enaml.editor.document import Document
from enaml.editor.testing_event_handler import TestingEventHandler


if __name__ == '__main__':
    app = QApplication([])

    with open(__file__, 'rb') as f:
        txt = f.read()

    # ~1.5 million lines
    doc = Document.from_string(txt * 50000)
    cursor = Cursor(doc)
    #cursor2 = Cursor(doc)
    #cursor2.move_down(3)
    e = QTextEditor()
    e.setDocument(doc)
    e.addCursor(cursor)
    #e.addCursor(cursor2)
    e.setEventHandler(TestingEventHandler())
    e.show()
    e.raise_()
    app.exec_()

