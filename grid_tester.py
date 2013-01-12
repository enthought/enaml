
from enaml.qt.qt.QtGui import QApplication
from enaml.grid.q_tabular_view import QTabularView
from enaml.grid.tabular_model import TabularModel


class MyModel(TabularModel):

    def row_count(self):
        return 10

    def column_count(self):
        return 10

    def data(self, rows, columns):
        for r in rows:
            for c in columns:
                yield (r, c)


if __name__ == '__main__':
    app = QApplication([])
    v = QTabularView()
    v.setModel(MyModel())
    v.show()
    app.exec_()
