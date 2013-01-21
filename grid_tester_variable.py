from enaml.qt.qt.QtCore import Qt
from enaml.qt.qt.QtGui import QApplication
from enaml.grid.q_tabular_view import QTabularView
from enaml.grid.tabular_model import TabularModel
from enaml.grid.q_fixed_size_header import QFixedSizeHeader
from enaml.grid.q_variable_size_header import QVariableSizeHeader


H_SCROLL = QTabularView.ScrollPerPixel

# Uncomment to scroll horizontally per-column
#H_SCROLL = QTabularView.ScrollPerItem

V_SCROLL = QTabularView.ScrollPerItem

# Uncomment to scroll vertically per-pixel
#V_SCROLL = QTabularView.ScrollPerPixel

# Set to True to use variable size cells
VARIABLE_SIZE_HEADER = True

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
        for r in rows:
            for c in columns:
                yield r + c

    def row_header_data(self, rows):
        for r in rows:
            yield 'Row %d' % r

    def column_header_data(self, columns):
        for c in columns:
            yield 'Column %d' % c

    row_sty = {
        'background': 'rgba(245, 245, 50, 0.5)'
    }

    def row_styles(self, rows):
        s = self.row_sty
        for r in rows:
            if r % 2:
                yield s
            else:
                yield None

    bold_font = {
        'family': 'arial',
        'weight': 'bold',
        'size': 12,
    }

    col_sty = {
        'background': 'rgba(0, 0, 255, 0.5)',
        'foreground': 'red',
        'font': bold_font,
        'border': {
            'style': 'dashed',
            'width': 2,
        },
        'margin': 5,
        'padding': 2,
    }

    def column_styles(self, columns):
        s = self.col_sty
        for c in columns:
            if c % 2:
                yield s
            else:
                yield None

    cell_sty = {
        'background': 'rgba(40, 60, 100, 0.7)',
        'foreground': 'lightskyblue',
        'font': {
            'style': 'italic'
        }
    }

    def cell_styles(self, rows, columns, data):
        s = self.cell_sty
        for d in data:
            if d % 7 == 0:
                yield s
            else:
                yield None


class VarModel(MyModel):
    def __init__(self, r=100, c=100):
        self.r = r
        self.c = c

    def row_count(self):
        """ something small for testing
        """
        return self.r

    def column_count(self):
        return self.c

if __name__ == '__main__':
    app = QApplication([])
    v = QTabularView()
    v._updateViewportMargins() # XXX make this automatic
    #v.setVerticalLinesVisible(False)
    #v.setHorizontalLinesVisible(False)
    v.setHorizontalScrollPolicy(H_SCROLL)
    v.setVerticalScrollPolicy(V_SCROLL)
    if VARIABLE_SIZE_HEADER:
        # uses QVariableSizeHeader
        col = 1000000
        row = 1000000
        v.setModel(VarModel(row, col))
        v.setRowHeader(QVariableSizeHeader(Qt.Vertical))
        v.setColumnHeader(QVariableSizeHeader(Qt.Horizontal))
        c_size = [30 + 10 * (x % 4) for x in xrange(col)]
        # also works to set constant size:
        #c_size = 30
        v.rowHeader().setSectionSize(c_size)
        r_size = [60 + 60 * (x % 3) for x in xrange(row)]
        #r_size = 60
        v.columnHeader().setSectionSize(r_size)
    else:
        # uses QFixedSizeHeader
        v.setModel(MyModel())
        v.rowHeader().setSectionSize(30)
    v.rowHeader().setHeaderSize(100)
    v.show()
    app.exec_()
