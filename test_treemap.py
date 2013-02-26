import datetime

import numpy as np
import pandas

from enaml.qt.qt.QtCore import QRect
from enaml.qt.qt.QtGui import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel
        )

from enaml.grid.pivot import pandas_pivot, pivot_ui, pivot_selector, treemap

np.random.seed(0)

dtype = np.dtype([
    ("Index", object),
    ("Symbol", object),
    ("Year", int),
    ("Month", int),
    ("Day", int),
    ("Quantity", int),
    ("Price", float),
])


def generateData(n=10000, prng=np.random):
    """ Generator function for a random set of superficially realistic data

    The parameter n is the number of rows to generate.
    """
    products = np.array([
        ('SP500', 'ADBE'),
        ('SP500', 'NVDA'),
        ('SP500', 'ORCL'),
        ('SP500', 'ADT'),
        ('SP100', 'ABT'),
        ('SP100', 'BRK.B'),
        ('SP100', 'AFSS'),
        ('SP100', 'AZ'),
        ('NDQ100', 'AAPL'),
        ('NDQ100', 'MSFT'),
        ('NDQ100', 'GOOG'),
        ('NDQ300', 'BLK'),
        ('NDQ300', 'CSCO'),
        ('NDQ300', 'COP'),
        ('FTSE', 'DGE.L'),
        ('FTSE', 'TSCO.L'),
        ('FTSE', 'GSK.L'),
    ], dtype=[('Index', object), ('Symbol', object)])
    items = np.empty(n, dtype=dtype)
    iproduct = prng.randint(0, len(products), n)
    items['Index'] = products['Index'][iproduct]
    items['Symbol'] = products['Symbol'][iproduct]
    dr = np.array([datetime.date.fromordinal(i) for i in
        range(datetime.date(2000, 1, 1).toordinal(), datetime.date(2010, 12, 31).toordinal())],
        dtype=object)
    dates = dr[prng.randint(0, len(dr), n)]
    items['Year'] = [d.year for d in dates]
    items['Month'] = [d.month for d in dates]
    items['Day'] = [d.day for d in dates]
    items['Quantity'] = prng.randint(1, 101, n)
    items['Price'] = prng.lognormal(4.0, 2.0, n)
    return items


def getdf(n=10000, prng=np.random):
    a = generateData(n, prng)
    return pandas.DataFrame(a)

def main():
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-n', '--nrows', type=int, default=10000, help='The number of rows')

    args = parser.parse_args()
    app = QApplication([])
    frame = getdf(args.nrows)
    print 'Generated data.'
    engine = pandas_pivot.PandasEngine.from_frame(frame, 
        aggregates = [('Revenue', 'sum'), ('Price', 'geo_mean'), ('Quantity', sum)],
        #aggregates = [('Revenue', 'sum')],
        row_pivots = ['Index', 'Symbol'],
        #row_pivots = [], #'Year', 'Month', 'Day'],
        col_pivots = [],
        #col_pivots = ['Year'],
        extra_columns = [('Revenue', 'Quantity*Price')],
        #filter_expr = 'Quantity < 10',
        #row_expand_depth = 3,
        shade_depth = True,
        row_margins = 'before',
        col_margins = 'before',
    )

    tv = pivot_ui.table_view(engine)
    tv.setHorizontalScrollPolicy(tv.ScrollPerItem)
    tv.setVerticalScrollPolicy(tv.ScrollPerItem)

    tm = treemap.treemap_view(engine)

    selector = pivot_selector.PivotSelector()
    selector.setSelectors(engine.row_pivots)

    def update_pivots(sel):
        tm.setDepth(sel+1)

    selector.selectorLevelChanged.connect(update_pivots)

    win = QWidget()
    l = QHBoxLayout()
    l.addWidget(selector)
    l.addStretch()
    layout = QVBoxLayout()
    layout.addLayout(l)
    layout.addWidget(tv)
    layout.addWidget(tm)
    win.setLayout(layout)
    win.setGeometry(QRect(200, 200, 800, 600))
    win.show()
    app.exec_()

if __name__ == '__main__':
    main()
