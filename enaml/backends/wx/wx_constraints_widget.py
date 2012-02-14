#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .wx_widget_component import WXWidgetComponent

from ...components.constraints_widget import AbstractTkConstraintsWidget


class WXConstraintsWidget(WXWidgetComponent, AbstractTkConstraintsWidget):
    """ A Wx implementation of ConstraintsWidget.

    """
    pass

