#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .constraints_widget import ConstraintsWidget


class Control(ConstraintsWidget):
    """ A widget which represents a leaf node in the hierarchy.

    A Control is conceptually the same as a ConstraintsWidget, except
    that it does not have widget children. This base class serves as
    a placeholder for potential future functionality.

    """
    pass

