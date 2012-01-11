#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from .menu_bar import MenuBar
from .window import Window, AbstractTkWindow


class AbstractTkMainWindow(AbstractTkWindow):
    """ The abstract toolkit interface for a MainWindow.

    """
    pass


class MainWindow(Window):
    """ A declarative Enaml Component which represents a main window.

    """
    #: A read-only property which holds the declarative MenuBar, or
    #: None if one is not provided. If more than one MenuBar is given,
    #: the one which is most recently defined takes precedence.
    menu_bar = Property(depends_on='children')

    @cached_property
    def _get_menu_bar(self):
        """ The property getter for the 'menu_bar' attribute.

        """
        flt = lambda child: isinstance(child, MenuBar)
        res = filter(flt, self.children)
        if len(res) == 0:
            res = None
        else:
            res = res[-1]
        return res

