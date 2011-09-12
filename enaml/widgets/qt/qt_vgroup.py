from traits.api import implements

from .qt_group import QtGroup

from ..vgroup import IVGroupImpl


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
    
    # IVGroupImpl interface is empty and fully implemented by WXGroup

    # XXX should we change implementation to use QVBoxLayout