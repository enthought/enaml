#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .constraints_widget import ConstraintsWidget


class Control(ConstraintsWidget):
    """ A widget which represents a leaf node in the hierarchy.

    A Control is conceptually the same as a ConstraintsWidget, except
    that it is not allowed to have children.

    """
    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def validate_children(self, children):
        """ A child validator which rejects all children.

        """
        if children:
            name = type(self).__name__
            msg = 'Cannot add children to a component of type `%s`'
            raise ValueError(msg % name)
        return children

