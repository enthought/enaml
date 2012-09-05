#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasTraits, Any, on_trait_change

from chaco.api import (ArrayPlotData, ArrayDataSource, DataRange1D, 
                       LinearMapper, VPlotContainer, PlotAxis, FilledLinePlot, 
                       add_default_grids, Plot)
from chaco.tools.api import RangeSelection
from chaco.scales.api import CalendarScaleSystem
from chaco.scales_tick_generator import ScalesTickGenerator

from zoom_overlay import ZoomOverlay


class PlotDriver(HasTraits):

    model = Any

    def __init__(self, model):
        super(PlotDriver, self).__init__(model=model)

    @on_trait_change('model:data')
    def update_plots(self, data):
        self.close_plot.index.set_data(data['dates'])
        self.close_plot.value.set_data(data['close'])
        self.low_plot.index.set_data(data['dates'])
        self.low_plot.value.set_data(data['low'])
        self.bar_plot.index.set_data(data['dates'])
        self.bar_plot.value.set_data(data['volume'])
        self.close_plot.controller.deselect()

    def get_plot_component(self):
        # Create the array plot data that will feed our plots
        data = self.model.data
        plot_data = ArrayPlotData(index=data['dates'], 
                                  close=data['close'],
                                  volume=data['volume'],)
        self.plot_data = plot_data
        
        # Need to make the FilledLinePlot manually since Plot doesn't
        # support that plot type.
        times = ArrayDataSource(data['dates'])
        prices = ArrayDataSource(data['close'])
        close_plot =  FilledLinePlot(index=times, value=prices,
                        index_mapper = LinearMapper(range=DataRange1D(times)),
                        value_mapper = LinearMapper(range=DataRange1D(prices)),
                        edge_color = 'blue',
                        face_color = 'paleturquoise',
                        bgcolor = 'white',
                        border_visible = True)
        close_plot.padding = [40, 15, 15, 20]
        self.close_plot = close_plot

        # The second plotter object which generates our candle plot
        plotter2 = Plot(data=plot_data)
        low_plot = plotter2.plot(('index', 'close'),)[0]
        low_plot.height = 100
        low_plot.resizable = 'h'
        low_plot.bgcolor = 'white'
        low_plot.border_visible = True
        low_plot.padding = [40, 15, 15, 20]
        low_plot.color = 'darkred'
        low_plot.line_width = 1.5
        self.low_plot = low_plot

        # The third plotter for the bar plot.
        plotter3 = Plot(data=plot_data)
        bar_plot = plotter3.plot(('index', 'volume'), type='bar')[0]
        bar_plot.height = 100
        bar_plot.resizable = 'h'
        bar_plot.bgcolor = 'white'
        bar_plot.border_visible = True
        bar_plot.padding = [40, 15, 15, 20]
        bar_plot.line_color = 'transparent'
        bar_plot.fill_color = 'black'
        bar_plot.bar_width = 3.0
        bar_plot.bar_width_type = 'screen'
        bar_plot.antialias = False
        bar_plot.index_mapper = low_plot.index_mapper
        self.bar_plot = bar_plot
    
        for plot in (close_plot, low_plot, bar_plot):
            ticker = ScalesTickGenerator(scale=CalendarScaleSystem())
            bottom_axis = PlotAxis(plot, orientation='bottom', 
                                   tick_generator=ticker)
            plot.overlays.append(bottom_axis)
            plot.overlays.append(PlotAxis(plot, orientation='left'))
            hgrid, vgrid = add_default_grids(plot)
            vgrid.tick_generator = bottom_axis.tick_generator
        
        def vol_label_formatter(val):
            return '%.1E' % val
        
        bar_plot.overlays[-1].tick_label_formatter = vol_label_formatter

        container = VPlotContainer(
            bgcolor=(240/255., 240/255., 240/255., 1.0),
            spacing=20,
            padding=20,
            fill_padding=True,
            stack_order='top_to_bottom',
            use_back_buffer=True,
        )

        container.add(close_plot)
        container.add(low_plot)
        container.add(bar_plot)

        close_plot.controller = RangeSelection(close_plot)
        zoom_overlay = ZoomOverlay(source=close_plot, destination=low_plot,
                                   other=bar_plot)
        container.overlays.append(zoom_overlay)

        return container

