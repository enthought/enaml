#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Str, Instance, Property, cached_property

from .component import Component, AbstractTkComponent
from .layout_component import LayoutComponent
from .layout_task_handler import LayoutTaskHandler


class AbstractTkWindow(AbstractTkComponent):
    """ The abstract ToplevelWindow interface.

    """
    @abstractmethod
    def shell_title_changed(self, title):
        """ Update the title of the window with the new value from the
        shell object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_central_widget_changed(self, central_widget):
        """ Update the central widget in the window with the new value
        from the shell object.

        """
        raise NotImplementedError


class Window(LayoutTaskHandler, Component):
    """ A top-level Window component.

    A Window component is represents of a top-level visible component
    with a frame decoration. It has exactly one central widget which
    is expanded to fit the size of the window. This class serves as
    the base class for MainWindow and Dialog. It is and abstract class
    and not meant to be used directly.

    """
    #: The title displayed on the window frame.
    title = Str

    #: A read-only property which holds the central widget. Declaring
    #: more than one central widget is an error.
    central_widget = Property(
        Instance(LayoutComponent), depends_on='children',
    )

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkWindow)

    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_central_widget(self):
        """ The property getter for the 'central_widget' attribute.

        """
        flt = lambda child: isinstance(child, LayoutComponent)
        widgets = filter(flt, self.children)
        n = len(widgets)
        if n > 1:
            msg = ('A MainWindow can have at most 1 central widget. '
                   'Got %s instead.')
            raise ValueError(msg % n)
        elif n == 0:
            res = None
        else:
            res = widgets[0]
        return res

    #--------------------------------------------------------------------------
    # Abstract Methods
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
        raise NotImplementedError
        
    def hide(self):
        """ Hide the window, but do not destroy the underlying widgets.

        """
        raise NotImplementedError

