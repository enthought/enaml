#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx.html

from .wx_constraints_widget import WxConstraintsWidget


class wxProperHtmlWindow(wx.html.HtmlWindow):
    """ A custom wx Html window that returns a non-braindead best size.

    """
    _best_size = wx.Size(256, 192)

    def GetBestSize(self):
        """ Returns the best size for the html window.

        """
        return self._best_size


class WxHtml(WxConstraintsWidget):
    """ A Wx implementation of the Enaml Html widget.

    """
    def create(self):
        """ Create the underlying widget.

        """
        self.widget = wxProperHtmlWindow(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the widget's attributes.

        """
        super(WxHtml, self).initialize(attrs)
        self.set_source(attrs['source'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_source(self, content):
        """ Handle the 'set_source' action from the Enaml widget.

        """
        self.set_source(content['source'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_source(self, source):
        """ Set the source of the html widget

        """
        self.widget.SetPage(source)

