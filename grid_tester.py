
from enaml.qt.qt.QtGui import QApplication
from enaml.grid.q_tabular_view import QTabularView
from enaml.grid.tabular_model import TabularModel


H_SCROLL = QTabularView.ScrollPerPixel

# Uncomment to scroll horizontally per-column
#H_SCROLL = QTabularView.ScrollPerItem

V_SCROLL = QTabularView.ScrollPerItem

# Uncomment to scroll vertically per-pixel
#V_SCROLL = QTabularView.ScrollPerPixel


negative_red = {
    'foreground': 'red',
    'background': 'lightskyblue',
    'align': 'left',
}


positive_blue = {
    'foreground': '#3344ee',
    'background': '#dddddd',
    'align': 'right',
}


class MyModel(TabularModel):

    def row_count(self):
        if V_SCROLL == QTabularView.ScrollPerPixel:
            r = 10000000
        else:
            r = (1 << 31) - 1 # max rows == 2,147,483,647
        return r

    def column_count(self):
        if H_SCROLL == QTabularView.ScrollPerPixel:
            r = 100
        else:
            r = (1 << 31) - 1 # max columns == 2,147,483,647
        return r

    def data(self, rows, columns):
        # uncomment to show requested data block size
        #print 'block size - rows: %d cols: %d' % (len(rows), len(columns))
        neg = negative_red
        pos = positive_blue
        for r in rows:
            for c in columns:
                v = r + c
                if v % 13 == 0 or v % 7 == 0:
                    yield (str(-v), neg)
                elif v % 4 == 0:
                    yield (str(v), pos)
                else:
                    yield (str(v), None)

    def horizontal_header_data(self, columns):
        for c in columns:
            yield 'Column %d' % c

    def vertical_header_data(self, rows):
        for r in rows:
            yield 'Row %d' % r


if __name__ == '__main__':
    app = QApplication([])
    v = QTabularView()
    v.setHorizontalScrollPolicy(H_SCROLL)
    v.setVerticalScrollPolicy(V_SCROLL)
    v.setModel(MyModel())
    v.show()
    app.exec_()

