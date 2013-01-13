
from enaml.qt.qt.QtGui import QApplication
from enaml.grid.q_tabular_view import QTabularView
from enaml.grid.tabular_model import TabularModel


H_SCROLL = QTabularView.ScrollPerPixel

# Uncomment to scroll horizontally per-column
#H_SCROLL = QTabularView.ScrollPerItem

V_SCROLL = QTabularView.ScrollPerItem

# Uncomment to scroll vertically per-pixel
#V_SCROLL = QTabularView.ScrollPerPixel


class MyModel(TabularModel):

    def row_count(self):
        if V_SCROLL == QTabularView.ScrollPerPixel:
            r = 10000000
        else:
            r = (1 << 31) - 1 # max rows == 2,147,483,647
        return r

    def column_count(self):
        return 100

    def data(self, rows, columns):
        # uncomment to show requested data block size
        #print 'block size - rows: %d cols: %d' % (len(rows), len(columns))
        for r in rows:
            for c in columns:
                yield str(r + c)


if __name__ == '__main__':
    app = QApplication([])
    v = QTabularView()
    v.setHorizontalScrollMode(H_SCROLL)
    v.setVerticalScrollMode(V_SCROLL)
    v.setModel(MyModel())
    v.show()
    app.exec_()

