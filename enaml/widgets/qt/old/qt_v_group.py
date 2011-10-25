#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import implements

from .qt_group import QtGroup

from ..v_group import IVGroupImpl


class QtVGroup(QtGroup):
    """ A Qt implementation of IVGroup.

    This is a convienence subclass of QtGroup which restricts the 
    layout direction to vertical.

    See Also
    --------
    IVGroup
    
    """ 
    implements(IVGroupImpl)

    #---------------------------------------------------------------------------
    # IVGroupImpl interface
    #---------------------------------------------------------------------------
    
    # IVGroupImpl interface is empty and fully implemented by QtGroup

    # XXX should we change implementation to use QVBoxLayout
