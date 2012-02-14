#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_widget_component import QtWidgetComponent

from ...components.constraints_widget import AbstractTkConstraintsWidget


class QtConstraintsWidget(QtWidgetComponent, AbstractTkConstraintsWidget):
    """ A Qt4 implementation of ConstraintsWidget.

    """
    pass

