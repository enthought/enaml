#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" An example which assembles a data-flow pipeline and connects the
output to a live chaco plot. The input of the pipeline can be driven
at several thousand Hz, while the output remains throttled at a rate
that is useful for a UI application.

"""
from math import sin

from chaco.api import (
    LinePlot, LinearMapper, DataRange1D, ArrayDataSource, PlotAxis,
    OverlayPlotContainer,
)

import enaml

from data_generator import DummyDataGenerator
from publisher import NumpyPublisher
from data_source import DataSource



class SinGenerator(object):
    """ A simple data generator which computes the sin of the timestamp
    for a given frequency.

    """
    def __init__(self, frequency=1.0):
        self.frequency = frequency
    
    def __call__(self, ts):
        return ('sin', sin(self.frequency * ts))


class ModGenerator(object):
    """ A simple data generator which mods a timestamp by a given
    amount.

    """
    def __init__(self, frequency=1.5):
        self.frequency = frequency
    
    def __call__(self, ts):
        return ('mod', ts % self.frequency)


if __name__ == '__main__':
    #--------------------------------------------------------------------------
    # Data Source Generation
    #--------------------------------------------------------------------------
    sin_gen = SinGenerator()
    mod_gen = ModGenerator()

    # Create reactive data generator
    reactive_data_generator = DummyDataGenerator(1000, sin_gen, mod_gen)

    # Create the data publishers
    sin_publisher = NumpyPublisher(
        reactive_data_generator, 'sin', frequency=30,
    )
    mod_publisher = NumpyPublisher(
        reactive_data_generator, 'mod', frequency=30,
    )

    # Create a data sources
    sin_data_source = DataSource(publisher=sin_publisher, buffer_size=2250)
    mod_data_source = DataSource(publisher=mod_publisher, buffer_size=2250)

    # Bind the data sources to their publishers
    sin_data_source.bind()
    mod_data_source.bind()

    #--------------------------------------------------------------------------
    # Plot Generation
    #--------------------------------------------------------------------------
    sin_index = ArrayDataSource([])
    sin_value = ArrayDataSource([])

    mod_index = ArrayDataSource([])
    mod_value = ArrayDataSource([])

    x_mapper = LinearMapper(range=DataRange1D(sin_index))
    y_mapper = LinearMapper(range=DataRange1D(sin_value))

    y_mapper.range.low_setting = -2.2
    y_mapper.range.high_setting = 2.2

    sin_line_plot = LinePlot(
        index=sin_index, value=sin_value, index_mapper=x_mapper, 
        value_mapper=y_mapper, color='darkblue',
    )

    mod_line_plot = LinePlot(
        index=mod_index, value=mod_value, index_mapper=x_mapper,
        value_mapper=y_mapper, color='darkred',
    )

    container = OverlayPlotContainer(
        bgcolor='white', padding=50, fill_padding=False, border_visible=True,
    )
    container.add(sin_line_plot)
    container.add(mod_line_plot)

    left_axis = PlotAxis(
        mapper=y_mapper, component=container, orientation='left',
    )
    container.overlays.append(left_axis)

    #--------------------------------------------------------------------------
    # View Generation
    #--------------------------------------------------------------------------
    # Import and create the viewer for the plot
    with enaml.imports():
        from updating_plot_view import PlotView

    view = PlotView(
        component=container, publishers=[sin_publisher, mod_publisher],
        data_sources=[sin_data_source, mod_data_source],
        feed=reactive_data_generator, mod_gen=mod_gen, sin_gen=sin_gen,
    )

    # Create a subscription function that will update the plot on the
    # main gui thread.
    def sin_update_func(data):
        def closure():
            sin_line_plot.index.set_data(data['index'])
            sin_line_plot.value.set_data(data['value'])
        view.toolkit.app.call_on_main(closure)

    def mod_update_func(data):
        def closure():
            mod_line_plot.index.set_data(data['index'])
            mod_line_plot.value.set_data(data['value'])
        view.toolkit.app.call_on_main(closure)
    
    # Attach the update functions to the data sources
    sin_data_source.subscribe(sin_update_func)
    mod_data_source.subscribe(mod_update_func)

    # Start the publisher's event loops
    sin_publisher.start()
    mod_publisher.start()

    # Schedule the data generator to start once the ui is up and
    # running
    view.toolkit.app.schedule(reactive_data_generator.start)

    def closed_cb():
        # Shut.Down.Everything
        reactive_data_generator.stop()
        sin_publisher.stop()
        mod_publisher.stop()
    
    # Assign the callback to be called when the window is closed.
    view.closed_cb = closed_cb

    # Start the application.
    view.show()

