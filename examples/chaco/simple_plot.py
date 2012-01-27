#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A simple Chaco Plot Component.

"""
import functools

from chaco.api import ArrayPlotData
from chaco.tools.api import PanTool, ZoomTool
from chaco.shell.scaly_plot import ScalyPlot
from chaco.scales.api import CalendarScaleSystem
from traits.api import (
    Array, Bool, DelegatesTo, Dict, Enum, Instance, List, Str, on_trait_change,
)

from enaml.core.toolkit import Toolkit
from enaml.widgets.enable_canvas import EnableCanvas


class DeferredCall(object):
    def __init__(self, obj, func, *args, **kwds):
        self.obj = obj
        self.func = func
        self.args = args
        self.kwds = kwds

    def __call__(self):
        return self.func(self.obj, *self.args, **self.kwds)


def plot_command(func):
    """ Create an object that represents a call to a method on a Plot 
    object.

    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwds):
        return DeferredCall(self, func, *args, **kwds)
    return wrapper


class SimplePlot(EnableCanvas):
    """ A Component that encapsulates a simple Chaco Plot.

    """

    #: The data.
    data = Dict(Str, Array)

    #: Titles.
    title = Str()
    xtitle = Str()
    ytitle = Str()

    #: The axis scales.
    xscale = Enum('linear', 'time', 'log')
    yscale = Enum('linear', 'time', 'log')

    #: Whether to show the legend or not.
    legend = Bool(False)

    #: The list of commands to execute on the Plot object.
    commands = List(Instance(DeferredCall))

    #: The plot data object.
    plot_data = Instance(ArrayPlotData, ())

    #: The plot object.
    component = Instance(ScalyPlot)
    def _component_default(self):
        plot = ScalyPlot(self.plot_data)
        return plot

    #: Delegates.
    bgcolor = DelegatesTo('component')
    default_origin = DelegatesTo('component')
    orientation = DelegatesTo('component')
    padding_top = DelegatesTo('component')
    padding_bottom = DelegatesTo('component')
    padding_left = DelegatesTo('component')
    padding_right = DelegatesTo('component')
    padding = DelegatesTo('component')
    border_visible = DelegatesTo('component')
    title = DelegatesTo('component')
    title_font = DelegatesTo('component')
    title_position = DelegatesTo('component')
    title_text = DelegatesTo('component')
    title_color = DelegatesTo('component')
    title_angle = DelegatesTo('component')
    legend_alignment = DelegatesTo('component')


    @classmethod
    def activate(cls):
        """ Add this component to the active toolkit.

        """
        tk = Toolkit.active_toolkit()
        cons = tk['EnableCanvas'].clone(shell_loader=lambda:cls)
        tk[cls.__name__] = cons

    def _setup_init_widgets(self):
        super(SimplePlot, self)._setup_init_widgets()
        self.set_data()
        self.set_commands()
        self._xtitle_changed(self.xtitle)
        self._ytitle_changed(self.ytitle)
        self._title_changed(self.title)

    @on_trait_change('commands[]')
    def set_commands(self):
        """ Execute the commands on the plot.

        """
        for command in self.commands:
            command()

    @on_trait_change('data[]')
    def set_data(self):
        for name, array in self.data.iteritems():
            self.plot_data.set_data(name, array)

    @plot_command
    def plot(self, *args, **kwds):
        self.component.plot(*args, **kwds)

    @plot_command
    def img_plot(self, *args, **kwds):
        self.component.img_plot(*args, **kwds)

    @plot_command
    def contour_plot(self, *args, **kwds):
        self.component.contour_plot(*args, **kwds)

    @plot_command
    def semilogx(self, *args, **kwds):
        kwds['index_scale'] = 'log'
        self.component.plot(*args, **kwds)

    @plot_command
    def semilogy(self, *args, **kwds):
        kwds['value_scale'] = 'log'
        self.component.plot(*args, **kwds)

    @plot_command
    def loglog(self, *args, **kwds):
        kwds['index_scale'] = 'log'
        kwds['value_scale'] = 'log'
        self.component.plot(*args, **kwds)

    @plot_command
    def xaxis(self, **kwds):
        self.component.x_axis.trait_set(**kwds)
        self.component.request_redraw()

    @plot_command
    def yaxis(self, **kwds):
        self.component.y_axis.trait_set(**kwds)
        self.component.request_redraw()

    @plot_command
    def xrange(self, **kwds):
        self.component.index_range.trait_set(**kwds)

    @plot_command
    def yrange(self, **kwds):
        self.component.value_range.trait_set(**kwds)

    @plot_command
    def pan_tool(self, **kwds):
        self.component.tools.append(PanTool(self.component, **kwds))

    @plot_command
    def zoom_tool(self, **kwds):
        self.component.overlays.append(ZoomTool(self.component, **kwds))

    def _xtitle_changed(self, new):
        self.component.x_axis.title = new
        self.component.request_redraw()

    def _ytitle_changed(self, new):
        self.component.y_axis.title = new
        self.component.request_redraw()

    def _title_changed(self, new):
        self.component.title = new
        self.component.request_redraw()

    def _set_scale(self, axis, system):
        p = self.component
        if axis == 'x':
            log_linear_trait = 'index_scale'
            ticks = p.x_ticks
        else:
            log_linear_trait = 'value_scale'
            ticks = p.y_ticks
        if system == 'time':
            system = CalendarScaleSystem()
        if isinstance(system, basestring):
            setattr(p, log_linear_trait, system)
        else:
            if system is None:
                system = dict(linear=p.linear_scale, log=p.log_scale).get(
                    p.get(log_linear_trait), p.linear_scale)
            ticks.scale = system
        p.request_redraw()

    def _xscale_changed(self, new):
        self._set_scale('x', new)

    def _yscale_changed(self, new):
        self._set_scale('y', new)

    def _legend_changed(self, new):
        self.component.legend = new
        self.component.request_redraw()

    def _bgcolor_changed(self, new):
        self.component.request_redraw()

