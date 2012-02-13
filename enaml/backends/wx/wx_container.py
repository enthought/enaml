#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref

import wx

from .wx_layout_component import WXLayoutComponent

from ..container import AbstractTkContainer


class _WXPanel(wx.Panel):
    """ A subclass of wxPanel which calls back onto the shell Container 
    to get the size hint. If that size hint is invalid, it falls back 
    onto the Wx default.

    """
    def __init__(self, wx_container, *args, **kwargs):
        super(_WXPanel, self).__init__(*args, **kwargs)
        self.wx_container = weakref.ref(wx_container)

    def GetBestSizeTuple(self):
        """ Computes the size hint from the given Container, falling
        back on the default size hint computation if the Container 
        returns one that is invalid.

        """
        res = None
        wx_container = self.wx_container()
        if wx_container is not None:
            shell = wx_container.shell_obj
            if shell is not None:
                sh = shell.size_hint()
                if sh != (-1, -1):
                    res = sh
        if res is None:
            res = super(_WXPanel, self).GetBestSizeTuple()
        return res


class WXContainer(WXLayoutComponent, AbstractTkContainer):
    """ A Wx implementation of a Container.

    """
    def create(self, parent):
        """ Creates the underlying Wx widget.

        """
        self.widget = _WXPanel(self, parent)

    def bind(self):
        """ Bind the widget to the wx.EVT_SIZE.

        """
        super(WXContainer, self).bind()
        self.widget.Bind(wx.EVT_SIZE, self.on_resize)
    
    def on_resize(self, event):
        """ Triggers a relayout of the shell object since the component
        has been resized.

        """
        # Notice that we are calling refresh() here instead of 
        # request_refresh() since we want the refresh to happen
        # immediately. Otherwise the resize layouts will appear 
        # to lag in the ui. This is a safe operation since by the
        # time we get this resize event, the widget has already 
        # changed size. Further, the only geometry that gets set
        # by the layout manager is that of our children. And should
        # it be required to resize this widget from within the layout
        # call, then the layout manager will do that asynchronously.
        self.shell_obj.refresh()

        # We need to call event.Skip() here or certain controls won't
        # won't inform their children to resize.
        event.Skip()

