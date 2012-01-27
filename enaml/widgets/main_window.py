#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance, Int, Property, cached_property

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
    
    @abstractmethod
    def menu_bar_height(self):
        """ Returns the height of the menu bar in pixels. If the menu
        bar does not have an effect on the height of the main window,
        this method returns Zero.

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
        
    #: A private read-only cached property that returns the height
    #: of the menu bar.
    _menu_bar_height = Property(Int, depends_on='menu_bar')

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

    @cached_property
    def _get__menu_bar_height(self):
        """ The property getter for the '_menu_bar_height' attribute.

        """
        if self.menu_bar is not None:
            res = self.abstract_obj.menu_bar_height()
        else:
            res = 0
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
            self.resize_to_initial()
            self.update_minimum_size()
            self.update_maximum_size()
        # Some Gui's don't like to process all events from a single 
        # call to process events (Qt), and pumping the loop is not
        # reliable. Instead, we just schedule the call to set_visible 
        # to occur after we start the event loop and with a priority 
        # that is less than any relayouts the may be triggered by 
        # pending events. This means that the layout queue should 
        # finish processing, and then the window will be shown.
        app.schedule(self.set_visible, (True,), priority=75)
        app.start_event_loop()
        
    def hide(self):
        """ Hide the window, but do not destroy the underlying widgets.

        """
        self.set_visible(False)

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def _menu_bar_changed(self):
        """ Updates the minimum and maximum sizes of main window if the
        menu bar changes after the window has been initialized.

        """
        self.request_relayout_task(self.update_minimum_size)
        self.request_relayout_task(self.update_maximum_size)

    #--------------------------------------------------------------------------
    # Parent Class Overrides
    #--------------------------------------------------------------------------
    def _compute_initial_size(self):
        """ Overridden parent class method to add the sizes of any of
        the non-central-widget children to the computed initial size.

        """
        width, height = super(MainWindow, self)._compute_initial_size()
        height += self._menu_bar_height
        return (width, height)

    def _compute_minimum_size(self):
        """ Overridden parent class method to add the sizes of any of
        the non-central-widget children to the computed minimum size.

        """
        width, height = super(MainWindow, self)._compute_minimum_size()
        height += self._menu_bar_height
        return (width, height)
    
    def _compute_maximum_size(self):
        """ Overridden parent class method to add the sizes of any of
        the non-central-widget children to the computed maximum size.

        """
        width, height = super(MainWindow, self)._compute_maximum_size()
        height += self._menu_bar_height
        return (width, height)

