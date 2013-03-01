import datetime

import numpy as np
import pandas

from enaml.qt.qt.QtCore import QRect
from enaml.qt.qt.QtGui import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QRadioButton,
        QButtonGroup,
        )

from enaml.grid.pivot import pandas_pivot, pivot_ui, pivot_selector, treemap

def main():
    app = QApplication([])
    frame = pandas.read_csv('StocksStatic.csv')
    engine = pandas_pivot.PandasEngine.from_frame(frame, 
        aggregates = [('Mcap(USD)', 'sum'), ('1 Week Change % (USD)', 'mean')],
        row_pivots = ['Industry', 'Supersector', 'Name'],
        col_pivots = [],
        row_margins = 'before',
        col_margins = 'before',
    )

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

    def changeStyle(b_id):
        tm.setStyle(group.checkedId())

    group = QButtonGroup()
    group.buttonClicked.connect(changeStyle)

    classic = QRadioButton("Classic")
    classic.setChecked(True)
    cluster = QRadioButton("Cluster")
    group.addButton(classic, 0)
    group.addButton(cluster, 1)
    l.addWidget(classic)
    l.addWidget(cluster)
    layout = QVBoxLayout()
    layout.addLayout(l)
    layout.addWidget(tm)
    win.setLayout(layout)
    win.setGeometry(QRect(400, 200, 870, 705))
    win.show()
    app.exec_()

if __name__ == '__main__':
    main()
