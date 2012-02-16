from chaco.api import (
    LinePlot, LinearMapper, DataRange1D, ArrayDataSource, PlotAxis,
    OverlayPlotContainer,
)
from chaco.scales.api import CalendarScaleSystem
from chaco.scales_tick_generator import ScalesTickGenerator

import enaml

from data_feed import DummyDataGenerator
from publisher import NumpyPublisher
from data_source import DataSource
from math import sin


def foo(timestamp, sawtooth):
    return sin(timestamp)

if __name__ == '__main__':
    #--------------------------------------------------------------------------
    # Data Source Generation
    #--------------------------------------------------------------------------
    # Create reactive data generator
    reactive_data_generator = DummyDataGenerator(1000, saw_freq=0.3)
    reactive_data_generator.start()

    # Create a data publisher
    numpy_publisher = NumpyPublisher(reactive_data_generator, frequency=30)
    other_numpy_publisher = NumpyPublisher(reactive_data_generator, frequency=30, mock_function=foo)
    # Start accepting data from the reactive data generator
    numpy_publisher.bind()
    other_numpy_publisher.bind()
    # Create a data source
    data_source = DataSource(publisher=numpy_publisher, buffer_size=2250, pass_through=False)
    other_data_source = DataSource(publisher=other_numpy_publisher, buffer_size=2250, pass_through=True)

    # Hooks up data source to start accepting data from the publisher
    data_source.bind()
    other_data_source.bind()

    #--------------------------------------------------------------------------
    # Plot Generation
    #--------------------------------------------------------------------------
    index = ArrayDataSource([])
    value = ArrayDataSource([])
    other = ArrayDataSource([])

    x_mapper = LinearMapper(range=DataRange1D(index))
    y_mapper = LinearMapper(range=DataRange1D(value))
    other_y_mapper = LinearMapper(range=DataRange1D(other))

    y_mapper.range.low_setting = -1.1
    y_mapper.range.high_setting = 1.1
    other_y_mapper.range.low_setting = -1.1
    other_y_mapper.range.high_setting = 1.1

    line_plot = LinePlot(
        index=index, value=value,
        index_mapper=x_mapper,
        value_mapper=y_mapper,
    )

    other_line_plot = LinePlot(
        index=index, value=other,
        index_mapper=x_mapper,
        value_mapper=other_y_mapper,
    )

    ticker = ScalesTickGenerator(scale=CalendarScaleSystem())
    container = OverlayPlotContainer(bgcolor='white', padding=50, fill_padding=False)
    container.add(line_plot)
    container.add(other_line_plot)

    bottom_axis = PlotAxis(mapper=x_mapper, component=container, orientation='bottom', tick_generator=ticker)
    left_axis = PlotAxis(mapper=y_mapper, component=container, orientation='left')

    container.overlays.append(bottom_axis)
    container.overlays.append(left_axis)

    #--------------------------------------------------------------------------
    # View Generation
    #--------------------------------------------------------------------------
    # Import and create the viewer for the plot
    with enaml.imports():
        from updating_plot_view import PlotView

    view = PlotView(
        component=container, publisher=numpy_publisher, data_source=data_source,
        feed=reactive_data_generator)

    # Create a subscription function that will update the plot on the
    # main gui thread.
    def update_func(data):
        def closure():
            line_plot.index.set_data(data['index'])
            line_plot.value.set_data(data['value'])
        view.toolkit.app.call_on_main(closure)

    def other_update_func(data):
        def closure():
            other_line_plot.index.set_data(data['index'])
            other_line_plot.value.set_data(data['value'])
        view.toolkit.app.call_on_main(closure)

    # Schedule a call to subcribe to the data feed once the view
    # is up and running.
    view.toolkit.app.schedule(data_source.subscribe, (update_func,))
    view.toolkit.app.schedule(other_data_source.subscribe, (other_update_func,))

    # Start the application.
    view.show()

    reactive_data_generator.stop()
    numpy_publisher.unbind()
