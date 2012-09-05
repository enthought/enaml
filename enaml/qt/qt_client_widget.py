#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_proxy_widget import QtProxyWidget
from .qt_constraints_widget import QtConstraintsWidget

class QtClientWidget(QtProxyWidget, QtConstraintsWidget):
    """ A Qt implementation of an Enaml ClientWidget.

    """
    pass
