#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_proxy_widget import WxProxyWidget
from .wx_constraints_widget import WxConstraintsWidget

class WxClientWidget(WxProxyWidget, WxConstraintsWidget):
    """ A Wx implementation of an Enaml ClientWidget.

    """
    pass
