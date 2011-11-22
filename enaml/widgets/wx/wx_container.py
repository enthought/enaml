#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_component import WXComponent

from ..container import AbstractTkContainer


class WXContainer(WXComponent, AbstractTkContainer):
    """ A wxPython implementation of Container.

    WXContainer is usually to be used as a base class for other container
    widgets. However, it may also be used directly as an undecorated 
    container for widgets for layout purposes.

    Notes
    -----
    - The default behaviour of the WXContainer is to return as it's size
      hint the tuple (-1, -1). This is valid for widgets that cannot
      determine a hint size.

    """
    def bind(self):
        """ Bind the widget to the wx.EVT_SIZE.

        """
        super(WXContainer, self).bind()
        self.widget.Bind(wx.EVT_SIZE, self.on_resize)

    def size_hint(self):
        """ Return default value (-1, -1) as a size hint for the generic
        containers in wx backend.

        """
        # XXX is this what we really want?
        return (-1, -1)
    
    def on_resize(self, event):
        """ Triggers a relayout of the shell object since the component
        has been resized.

        """
        # Notice that we are calling do_layout() here instead of 
        # set_needs_layout() since we want the layout to happen
        # immediately. Otherwise the resize layouts will appear 
        # to lag in the ui. This is a safe operation since by the
        # time we get this resize event, the widget has already 
        # changed size. Further, the only geometry that gets set
        # by the layout manager is that of our children. And should
        # it be required to resize this widget from within the layout
        # call, then the layout manager will do that via invoke_later.
        self.shell_obj.do_layout()

        # We need to call event.Skip() here or controls like 
        # wx.ChoiceBook won't inform their children to resize.
        event.Skip()

