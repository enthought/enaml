import datetime

from traits.api import HasTraits, List, Str, Date, Enum, Property, Array, Int, Tuple, on_trait_change

from enaml.factory import EnamlFactory

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


if __name__ == '__main__':
    model = HistoricData()
    plot_driver = PlotDriver(model)
    factory = EnamlFactory('./stock_view.enaml')
    view = factory(model=model, plot=plot_driver)
    view.show()

