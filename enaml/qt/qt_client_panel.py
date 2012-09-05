#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_proxy_widget import QtProxyWidget
from .qt_widget_component import QtWidgetComponent

class QtClientPanel(QtProxyWidget, QtWidgetComponent):
    """ A Qt implementation of an Enaml ClientPanel.

    """
    pass
