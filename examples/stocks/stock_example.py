#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import datetime

from traits.api import (
    HasTraits, List, Str, Date, Enum, Property, Array, Int, Tuple, 
    on_trait_change, Instance, Event, cached_property, DelegatesTo, Float,
)

import enaml
from enaml.item_models.abstract_item_model import AbstractTableModel
from enaml.styling.color import Color
from enaml.styling.brush import Brush

import stock_data
from plot_driver import PlotDriver

with enaml.imports():
    from stock_view import MainView


class HistoricData(HasTraits):

    available_symbols = List(Str)

    symbol = Enum(values='available_symbols')

    date_range = Tuple(Date, Date)

    end_date = Date

    days_of_history_choices = Property(depends_on='date_range')

    days_of_history = Enum(values='days_of_history_choices')

    start_date = Property(depends_on=['end_date', 'days_of_history'])

    num_points = Int(500)

    data = Array

    value = Float(42)

    def _available_symbols_default(self):
        return stock_data.get_symbols()

    def _date_range_default(self):
        return stock_data.get_symbol_date_range(self.symbol)

    def _end_date_default(self):
        return self.date_range[1] - datetime.timedelta(days=1)

    def _get_days_of_history_choices(self):
        start, end = self.date_range
        return range(100, (end - start).days, 100)

    def _get_start_date(self):
        return self.end_date - datetime.timedelta(days=self.days_of_history)

    def _compute_data(self):
        symbol = self.symbol
        start = self.start_date
        end = self.end_date
        num_points = self.num_points
        return stock_data.get_data(symbol, start, end, num_points)

    def _data_default(self):
        return self._compute_data()

    @on_trait_change('symbol')
    def _refresh_date_range(self, symbol):
        self.date_range = stock_data.get_symbol_date_range(symbol)

    @on_trait_change('symbol, start_date, end_date, num_points')
    def _refresh_data(self):
        self.data = self._compute_data()


class GridDataAdapter(HasTraits):

    model = Instance(HistoricData, ())

    data = DelegatesTo('model')

    available_columns = List(Str)

    grid_columns = List(Str)

    thresh = Property(depends_on='data')

    grid_size = Property(depends_on=['data', 'grid_columns'])

    grid_changed = Event

    def _available_columns_default(self):
        return ['open', 'close', 'low', 'high', 'volume']

    def _grid_columns_default(self):
        return ['open', 'close', 'low', 'high', 'volume']

    @cached_property
    def _get_grid_size(self):
        return (len(self.model.data), len(self.grid_columns))

    @on_trait_change('data, grid_columns')
    def grid_updated(self):
        self.grid_changed = True

    @cached_property
    def _get_thresh(self):
        data = self.data
        min = data['close'].min()
        max = data['close'].max()
        return 0.9 * (max - min) + min


HIGHLIGHT = Brush(Color.from_string('lightskyblue'), None)

TEXTCOLOR = Brush(Color.from_string('darkgray'), None)

NULLBRUSH = None


class StockDataTable(AbstractTableModel):

    def __init__(self, adapter):
        super(StockDataTable, self).__init__()
        self.adapter = adapter
        adapter.on_trait_change(self.refresh_table, 'grid_changed')

    def refresh_table(self):
        self.begin_reset_model()
        self.end_reset_model()

    def column_count(self, parent=None):
        if parent is None:
            return self.adapter.grid_size[1]
        return 0

    def row_count(self, parent=None):
        if parent is None:
            return self.adapter.grid_size[0]
        return 0
        
    def data(self, index):
        adapter = self.adapter
        data = adapter.data
        column = adapter.grid_columns[index.column]
        data = data[column][index.row]
        if data > 1e4:
            res = '%.2E' % data
        else:
            res = '%.2f' % data
        return res
    
    def background(self, index):
        adapter = self.adapter
        data = adapter.data['close'][index.row]
        if data > adapter.thresh:
            return HIGHLIGHT
        return NULLBRUSH
    
    def foreground(self, index):
        adapter = self.adapter
        data = adapter.data['close'][index.row]
        if data > adapter.thresh:
            return NULLBRUSH
        return TEXTCOLOR

    def vertical_header_data(self, section):
        data = self.adapter.data
        ts = data['dates'][section]
        return str(datetime.date.fromtimestamp(ts))
    
    def horizontal_header_data(self, section):
        return self.adapter.grid_columns[section].capitalize()


if __name__ == '__main__':
    model = HistoricData()
    plot_driver = PlotDriver(model)
    adapter = GridDataAdapter(model=model)
    data_table = StockDataTable(adapter)

    view = MainView(model, adapter, plot_driver, stock_data_table=data_table)
    view.show()

