import wx

from .wx_control import WxControl

import matplotlib
# We want matplotlib to use a wxPython backend
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_wx import NavigationToolbar2Wx


class WxMPLCanvas(WxControl):
    """ A Wx implementation of an Enaml MPLCanvas.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying mpl_canvas widget.

        """
        return wx.Panel(parent, -1, style=wx.CLIP_CHILDREN)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(WxMPLCanvas, self).create(tree)
        self.figure = tree['figure']

    def init_layout(self):
        """ A method that allows widgets to do layout initialization.

        This method is called after all widgets in a tree have had
        their 'create' method called. It is useful for doing any
        initialization related to layout.
        """
        figure = self.figure
        panel = self.widget()
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        # matplotlib commands to create a canvas
        if figure.canvas is None:
            mpl_control = FigureCanvas(panel, -1, figure)
        else:
            mpl_control = figure.canvas
        sizer.Add(mpl_control, 1, wx.LEFT | wx.TOP | wx.GROW)
        if not hasattr(mpl_control, 'toolbar'):
            toolbar = NavigationToolbar2Wx(mpl_control)
        else:
            toolbar = mpl_control.toolbar
        sizer.Add(toolbar, 0, wx.EXPAND)
        mpl_control.SetMinSize(mpl_control.GetSize())
        self.size_hint_updated()

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_figure(self, content):
        """ Handle the 'set_figure' action from the Enaml widget.

        """
        raise NotImplementedError
