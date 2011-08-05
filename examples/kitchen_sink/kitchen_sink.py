import numpy as np
from scipy.special import jv

from enthought.traits.api import HasTraits, Int, Instance, Str, Any, Enum, Property
from enthought.traits.ui.api import Item, View, Label, HGroup
from enthought.enable.api import ComponentEditor
from enthought.chaco.api import Plot, ArrayPlotData

from traitsml.view_factory import ViewFactory

from xray_plotlib import XRayOverlay, BoxSelectTool


#------------------------------------------------------------------------------
# A very simple model that is referenced as a context object in the tml
#------------------------------------------------------------------------------
class Model(HasTraits):

    x = Int(250)
    y = Int(50)
    
    width = Int(715)
    height = Int(735)

    button1_text = Str('I am button 1')

    def button1_clicked(self, arg):
        print 'button 1 clicked:', arg


#------------------------------------------------------------------------------
# The Traits UI plot that is embedded in the second tab of the tml view
#------------------------------------------------------------------------------
def sin_ladder(idx):
    return np.sin(idx) + np.linspace(0.0, 10.0, len(idx))


def cos_ladder(idx):
    return np.cos(idx) + np.linspace(10.0, 0.0, len(idx))


def bessel(idx):
    return jv(1.4, idx)


# This is the actual dialog bg color we want for the plot 
# component the default is a bit off.
BG_COLOR = (0.8980, 0.8980, 0.8980, 1.0)


class PlotUI(HasTraits):

    plot = Instance(Plot)
    
    data_funcs = {'Sin Ladder': sin_ladder,
                  'Cos Ladder': cos_ladder,
                  'Bessel': bessel}

    source_choice = Enum(sorted(data_funcs))

    value_func = Property(depends_on='source_choice')

    index = Instance(np.ndarray)

    value = Property(depends_on=['index', 'value_func'])

    traits_view = View(
                    HGroup(
                        Label('Select Source:'),
                        Item('source_choice', show_label=False),
                    ),
                    Item('plot', editor=ComponentEditor(bgcolor=BG_COLOR), 
                         show_label=False),
                    width=600, height=600,
                )
                     
    
    def __init__(self, *args, **kw):
        super(PlotUI, self).__init__(*args, **kw)
        
        plot_data = ArrayPlotData(index=self.index)
        plot_data.set_data('value', self.value)
        
        self.plot = Plot(plot_data)
        line = self.plot.plot(('index', 'value'))[0]
        
        line.overlays.append(XRayOverlay(line))
        line.tools.append(BoxSelectTool(line))
    
    def _index_default(self):
        return np.linspace(0.0, 25.0, 100)

    def _get_value_func(self):
        return self.data_funcs[self.source_choice]

    def _get_value(self):
        return self.value_func(self.index)

    def _value_changed(self, val):
        self.plot.data.set_data('value', val)
       
    def _index_changed(self, val):
        self.plot.data.set_index('index', val)

   
#------------------------------------------------------------------------------
# The app/controller which sets up the view and spawns the dialog if asked
#------------------------------------------------------------------------------
class Application(HasTraits):
    
    model = Instance(Model, ())
    plot_ui = Instance(PlotUI, ())

    factory = Any
    view = Any
    dialog = Any

    def _factory_default(self):
        return ViewFactory('./kitchen_sink.tml')

    def _view_default(self):
        return self.factory('main_container', model=self.model, 
                            controller=self, plot_ui=self.plot_ui)

    def _dialog_default(self):
        return self.factory('dialog', controller=self)

    def launch_dialog(self):
        self.dialog.show()

    def close_dialog(self):
        self.dialog.hide()

    def start(self):
        # This will go away at some point.
        from PySide import QtGui
        if not QtGui.QApplication.instance():
            app = QtGui.QApplication([])
        self.view.show()
        QtGui.QApplication.instance().exec_()

    
app = Application()
app.start()


