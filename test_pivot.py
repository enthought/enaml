import datetime

import numpy as np
import pandas

from enaml.qt.qt.QtCore import QRect
from enaml.qt.qt.QtGui import QApplication

from enaml.grid.pivot import pandas_pivot, pivot_ui

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
        ('NDQ100', 'AAPL'),
        ('NDQ100', 'MSFT'),
        ('NDQ100', 'GOOG'),
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
    frame = getdf(100) #args.nrows)
    print 'Generated data.'
    engine = pandas_pivot.PandasEngine.from_frame(frame, 
        #aggregates = [('Revenue', 'sum'), ('Price', 'geo_mean'), ('Quantity', sum)],
        aggregates = [('Price', 'mean')],
        row_pivots = ['Month', 'Day'],
        col_pivots = ['Index', 'Symbol', 'Year'],
        #extra_columns = [('Revenue', 'Quantity*Price')],
        #filter_expr = 'Quantity < 10',
        #row_expand_depth = 1,
        #col_expand_depth = 2,
        #row_expanded_paths = [(2,)],
        #col_expanded_paths = [('NDQ100', 'AAPL')],
        col_expanded_paths = [('FTSE', 'DGE.L')],
        shade_depth = True,
        row_margins='before',
        col_margins='before',
    )

    tv = pivot_ui.table_view(engine)
    tv.setGeometry(QRect(200, 200, 800, 600))
    tv.setHorizontalScrollPolicy(tv.ScrollPerItem)
    tv.setVerticalScrollPolicy(tv.ScrollPerItem)
    tv.show()
    app.exec_()

if __name__ == '__main__':
    main()
