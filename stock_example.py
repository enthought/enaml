import datetime

from traits.api import HasTraits, List, Str, Date, Enum, Property, Array, Int, Tuple, on_trait_change

from enaml.factory import EnamlFactory
from enaml.item_models.abstract_item_model import AbstractTableModel
from enaml.style_sheet import style
from enaml.enums import Orientation

import stock_data
from plot_driver import PlotDriver


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

    def update_bgcolor(self):
        global view
        ns = style('.error_colors', background_color='blue')
        view.style_sheet.update(ns)


class StockDataTable(AbstractTableModel):

    categories = ['open', 'high', 'low', 'close', 'volume']

    def __init__(self, model):
        super(StockDataTable, self).__init__()
        self.model = model
        self._data = model.data
        self.model.on_trait_change(self.refresh_table, 'data')

    def refresh_table(self, data):
        self._data = data
        self.notify_data_changed(-1, -1)
    
    def column_count(self, parent=None):
        return len(self.categories)

    def row_count(self, parent=None):
        return len(self._data)
    
    def data(self, index, role):
        category = self.categories[index.column]
        data = self._data[category][index.row]
        if data > 1e4:
            res = '%.2E' % data
        else:
            res = '%.2f' % data
        return res

    def header_data(self, section, orientation, role):
        if orientation == Orientation.VERTICAL:
            ts = self._data['dates'][section]
            return str(datetime.date.fromtimestamp(ts))
        else:
            return self.categories[section].capitalize()


if __name__ == '__main__':
    model = HistoricData()
    plot_driver = PlotDriver(model)
    data_table = StockDataTable(model)
    factory = EnamlFactory('./stock_view.enaml')
    view = factory(model=model, plot=plot_driver, stock_data_table=data_table)
    view.show()
    
