from chaco.api import (
    LinePlot, LinearMapper, DataRange1D, ArrayDataSource, PlotAxis, 
    VPlotContainer,
)
from chaco.scales.api import CalendarScaleSystem
from chaco.scales_tick_generator import ScalesTickGenerator

import enaml

from data_feed import DummyDataGenerator
from publisher import NumpyPublisher
from data_source import DataSource


if __name__ == '__main__':
    #--------------------------------------------------------------------------
    # Data Source Generation
    #--------------------------------------------------------------------------
    # Create reactive data generator
    reactive_data_generator = DummyDataGenerator(1 / 1500.0, 5)

    # Create a data publisher
    numpy_publisher = NumpyPublisher(reactive_data_generator, time_period=1/5.0)

    # Start accepting data from the reactive data generator
    numpy_publisher.bind()

    # Create a data source
    data_source = DataSource(publisher=numpy_publisher, buffer_size=10000)

    # Hooks up data source to start accepting data from the publisher
    data_source.bind()

    #--------------------------------------------------------------------------
    # Plot Generation
    #--------------------------------------------------------------------------
    index = ArrayDataSource([])
    value = ArrayDataSource([])
    line_plot = LinePlot(
        index=index, value=value, 
        index_mapper=LinearMapper(range=DataRange1D(index)),
        value_mapper=LinearMapper(range=DataRange1D(value)),
    )

    ticker = ScalesTickGenerator(scale=CalendarScaleSystem())
    bottom_axis = PlotAxis(line_plot, orientation='bottom', tick_generator=ticker)
    left_axis = PlotAxis(line_plot, orientation='left')
    
    line_plot.overlays.append(bottom_axis)
    line_plot.overlays.append(left_axis)

    container = VPlotContainer(bgcolor='white', padding=50, fill_padding=False)
    container.add(line_plot)

    #--------------------------------------------------------------------------
    # View Generation
    #--------------------------------------------------------------------------
    # Import cand create the viewer for the plot
    with enaml.imports():
        from updating_plot_view import PlotView
    view = PlotView(
        component=container, publisher=numpy_publisher, data_source=data_source,
    )

    # Create a subscription function that will update the plot on the
    # main gui thread.
    def update_func(data):
        def closure():
            line_plot.index.set_data(data['index'])
            line_plot.value.set_data(data['value'])
        view.toolkit.app.call_on_main(closure)
    
    # Schedule a call to subcribe to the data feed once the view 
    # is up and running.
    view.toolkit.app.schedule(data_source.subscribe, (update_func,))

    # Start the application.
    view.show()

