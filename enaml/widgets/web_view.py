#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode

from .control import Control


class WebView(Control):
    """ A widget which displays a web page.

    Unlike the simpler `Html` widget, this widget supports the features
    of a full web browser.

    """
    #: The URL to load in the web view. This can be a path to a remote
    #: resource or a path to a file on the local filesystem. This value
    #: is mutually exclusive of `html`.
    url = Unicode

    #: The html to load into the web view. This value is mutually
    #: exclusive of `url`.
    html = Unicode

    #: A web view expands freely in height and width by default.
    hug_width = 'ignore'
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Create the snapshot for the widget.

        """
        snap = super(WebView, self).snapshot()
        snap['url'] = self.url
        snap['html'] = self.html
        return snap

    def bind(self):
        """ Bind the change handlers for the widget.

        """
        super(WebView, self).bind()
        self.publish_attributes('url', 'html')

