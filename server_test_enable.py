from traits.api import HasTraits, Str, Property, Int, cached_property, Instance
import enaml
from enaml.application import Application
from enaml.session import Session
from enaml.qt.qt_local_server import QtLocalServer
from enaml.stdlib.sessions import view_factory

from numpy import sort
from numpy.random import random

# Chaco imports
from enable.api import Component
from chaco.api import ArrayPlotData, Plot
from chaco.tools.api import PanTool


#===============================================================================
# # Create the Chaco plot.
#===============================================================================
def _create_plot_component():

    # Create some data
    numpts = 5000
    x = sort(random(numpts))
    y = random(numpts)

    # Create a plot data obect and give it this data
    pd = ArrayPlotData()
    pd.set_data("index", x)
    pd.set_data("value", y)

    # Create the plot
    plot = Plot(pd)
    plot.plot(("index", "value"),
              type="scatter",
              marker="circle",
              index_sort="ascending",
              color="orange",
              marker_size=3,
              bgcolor="white")

    plot.tools.append(PanTool(plot))

    # Tweak some of the plot properties
    plot.title = "Scatter Plot"
    plot.line_width = 0.5
    plot.padding = 30

    return plot

class Model(HasTraits):
    
    value = Int(50)
    plot = Instance(Component)

    def _plot_default(self):
         return _create_plot_component()

@view_factory('foo-view')
def create_view(model):
    with enaml.imports():
        from server_test_enable import Main
    return Main(model=model)

if __name__ == '__main__':

    app_model = Model(text='Foo')
    app = Application([create_view(app_model)])

    server = QtLocalServer(app)

    client = server.local_client()
    client.start_session('foo-view')
    
    server.start()
