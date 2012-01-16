#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance, Property, cached_property

from .menu_bar import MenuBar
from .window import Window, AbstractTkWindow


class AbstractTkMainWindow(AbstractTkWindow):
    """ The abstract toolkit interface for a MainWindow.

    """
    @abstractmethod
    def shell_menu_bar_changed(self, menu_bar):
        """ Update the menu bar of the window with the new value from
        the shell object.

        """
        raise NotImplementedError
 

class MainWindow(Window):
    """ A top-level main window widget.

    MainWindow widgets are top-level widgets which provide various frame 
    decorations and other window related functionality. A window may 
    optionally contain a menubar, any number of toolbars, a status bar,
    and dock panes. A window can have at most one central widget child
    which will be expanded to fit the size of the window.

    """
    #: A read-only property which holds the MenuBar. If a MenuBar is not 
    #: declared, the value will be None. Declaring more than one MenuBar
    #: is an error.
    menu_bar = Property(Instance(MenuBar), depends_on='children')
        
    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_menu_bar(self):
        """ The property getter for the 'menu_bar' attribute.

        """
        flt = lambda child: isinstance(child, MenuBar)
        menu_bars = filter(flt, self.children)
        n = len(menu_bars)
        if n == 0:
            res = None
        elif n == 1:
            res = menu_bars[-1]
        else:
            msg = ('A MainWindow can have at most 1 MenuBar. '
                   'Got %s instead.')
            raise ValueError(msg % n)
        return res

    #--------------------------------------------------------------------------
    # Abstract Implementation Methods
    #--------------------------------------------------------------------------
    def show(self, parent=None):
        """ Make the window visible on the screen.

        If the window is not already fully initialized, then the 'setup'
        method will be called prior to making the window visible.

        Parameters
        ----------
        parent : native toolkit widget, optional
            Provide this argument if the window should have another
            widget as its logical parent. This may help with stacking
            order and/or visibility hierarchy depending on the toolkit
            backend.

        """
        app = self.toolkit.app
        app.initialize()
        if not self.initialized:
            self.setup(parent)
            # XXX expose initial sizes
            #size = (200, 100)
            #self.resize(*size)
        self.set_visible(True)
        app.start_event_loop()
        
    def hide(self):
        """ Hide the window, but do not destroy the underlying widgets.

        """
        self.set_visible(False)

