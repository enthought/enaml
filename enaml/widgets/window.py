#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import (
    Str, Instance, Property, cached_property, Tuple, Range, 
)

from .component import Component, AbstractTkComponent
from .container import Container
from .layout_component import LayoutComponent
from .layout_task_handler import LayoutTaskHandler
from .sizable import Sizable, AbstractTkSizable


# The set of strengths that are equal to, or stronger than, the resize
# strength of the window. This affects how the minimum and maximum 
# sizes of the window are computed.
STRONGER_THAN_RESIZE = set(('medium', 'strong', 'required'))


class AbstractTkWindow(AbstractTkComponent, AbstractTkSizable):
    """ The abstract ToplevelWindow interface.

    """
    @abstractmethod
    def maximize(self):
        """ Maximizes the window to fill the screen.

        """
        raise NotImplementedError
    
    @abstractmethod
    def minimize(self):
        """ Minimizes the window to the task bar.

        """
        raise NotImplementedError
    
    @abstractmethod
    def normalize(self):
        """ Restores the window after it has been minimized or maximized.

        """
        raise NotImplementedError

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


class Window(LayoutTaskHandler, Component, Sizable):
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
    
    #: The initial size to set the window on the first call show()
    #: If the initial size is set to (-1, -1), then a default value
    #: will be computed more-or-less intelligently. This attribute
    #: is only used the first time the window is shown to the screen.
    #: Further changes to the attribute will have no effect. The
    #: constituent values must be >= -1. The default is (-1, -1).
    initial_size = Tuple(Range(-1), Range(-1))
    
    #: The initial size of the window to use if the attempt to compute
    #: one intelligently fails. This is the "last resort" of determining
    #: the initial size. The constituent values must be >= 0. The 
    #: default is (200, 100).
    initial_size_default = Tuple(Range(0, value=200), Range(0, value=100))

    #: The minimum size allowable for the window. If the min size is 
    #: set to (-1, -1), then the minimum will be computed based on
    #: the children of the window, and in such cases the minimum size
    #: that is in use can be retrieved with the min_size() method.
    #: The constituent values must be >= -1. The default is (-1, -1).
    minimum_size = Tuple(Range(-1), Range(-1))

    #: The minimum size of the window to use if the attempt to compute
    #: one intelligently fails. This is the "last resort" of determining
    #: the minimum size. The constituent values must be >= 0. The 
    #: default is (0, 0).
    minimum_size_default = Tuple(Range(0), Range(0))

    #: The maximum size allowable for the window. If the max size is 
    #: set to (-1, -1), then the maximum will be computed based on
    #: the children of the window, and in such cases the maximum size
    #: that is in use can be retrieved with the max_size() method.
    #: The consituent values must be >= -1. The default is (-1, -1).
    maximum_size = Tuple(Range(-1), Range(-1))

    #: The maximum size of the window to use if the attempt to compute
    #: one intelligently fails. This is the "last resort" of determining
    #: the minimum size. The constituent values must be >= 0. The 
    #: default is (2**24 - 1, 2**24 - 1)
    maximum_size_default = Tuple(Range(0, value=(2**24 - 1)), 
                                 Range(0, value=(2**24 - 1)))

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
    
    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def _minimum_size_changed(self):
        """ Resets the minimum size of the window if the user provides
        a new value after initialization.

        """
        self.update_minimum_size()
    
    def _maximum_size_changed(self):
        """ Resets the maximum size of the window if the user provides
        a new value after initialization.

        """
        self.update_maximum_size()

    def _on_layout_deps_changed(self):
        """ A change handler for triggering a relayout when any of the
        layout dependencies change. It simply requests a relayout.

        """
        self.request_relayout()

    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def _setup_init_layout(self):
        """ A reimplemented parent class setup method that performs any
        layout initialization necessary for the window. The layout is
        initialized from the bottom up.

        """
        # This is identical to the code in LayoutComponent, but that
        # class also comes with constraints baggage that we don't need.
        # Hence, we just copy-paste this one small bit.
        super(Window, self)._setup_init_layout()
        self.initialize_layout()

    def initialize_layout(self):
        """ Hooks up change handlers for child attributes which will cause 
        a change in the layout.

        """
        self.on_trait_change(
            self._on_layout_deps_changed, (
                'central_widget:visible, '
                'central_widget:size_hint_updated, '
            )
        )

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def do_relayout(self):
        """ A reimplemented LayoutTaskHandler handler method which will
        perform necessary update activity when a relayout it requested.

        """
        # This method is called whenever a relayout is requested. By
        # default, this when the layout children change. In that case
        # we just need to update the min and max sizes. We are a top
        # level window, so no one really cares about our size hint. 
        self.update_minimum_size()
        self.update_maximum_size()

    #--------------------------------------------------------------------------
    # Auxiliary Methods
    #--------------------------------------------------------------------------
    def maximize(self):
        """ Maximizes the window to fill the screen.

        """
        self.abstract_obj.maximize()
            
    def minimize(self):
        """ Minimizes the window to the task bar.

        """
        self.abstract_obj.minimize()
            
    def normalize(self):
        """ Restores the window after it has been minimized or maximized.

        """
        self.abstract_obj.normalize()

    def resize_to_initial(self):
        """ Resizes the window to the computed initial size, provided 
        that the window has been initialized.

        """
        if self.initialized:
            init_size = self._compute_initial_size()
            self.resize(*init_size)

    def update_minimum_size(self):
        """ Updates the minimum size of the window based on its computed
        value, provided that the window has been initialized. This may 
        result in a resize if the computed value is more than the current
        size.

        """
        if self.initialized:
            min_size = self._compute_minimum_size()
            self.set_min_size(*min_size)

    def resize_to_minimum(self):
        """ Resizes the window to the computed minimum size, provided 
        that the window has been initialized.

        Note: This is not equivalent to making the window minimize
            into the task bar. For that, use the 'minimize()' method.

        """
        if self.initialized:
            min_size = self._compute_minimum_size()
            self.set_min_size(*min_size)
            self.resize(*min_size)
    
    def update_maximum_size(self):
        """ Updates the maximum size of the window based on its computed
        value, provided that the window has been initialized. This may 
        result in a resize if the computed value is less than the current
        size.

        """
        if self.initialized:
            max_size = self._compute_maximum_size()
            self.set_max_size(*max_size)

    def resize_to_maximum(self):
        """ Resizes the window to the computed maximum size, provided 
        that the window has been initialized. 

        Note: This is a potentially very expensive operation if the 
            maximum size is very large. This is not equivalent to 
            resizin a window to fit the screen. For that, use the 
            'maximize()' method.

        """
        if self.initialized:
            max_size = self._compute_maximum_size()
            self.set_max_size(*max_size)
            self.resize(*max_size)
    
    #--------------------------------------------------------------------------
    # Size Computation
    #--------------------------------------------------------------------------
    def _compute_initial_size(self):
        """ Computes and returns the initial size of the window without
        regard for minimum or maximum sizes.

        """
        # If the user has supplied an explicit initial size, use that.
        computed_width, computed_height = self.initial_size
        if computed_width != -1 and computed_height != -1:
            return (computed_width, computed_height)
        
        # Otherwise, try to compute a default from the central widget.
        widget = self.central_widget
        if widget is not None:
            size_hint_width, size_hint_height = widget.size_hint()
            if computed_width == -1:
                computed_width = size_hint_width
            if computed_height == -1:
                computed_height = size_hint_height

        # We use the last resort values to replace any remaining 
        # -1 values. This ensures the return value will be >= 0 
        # in both width and height.
        if computed_width == -1 or computed_height == -1:
            default_width, default_height = self.initial_size_default
            if computed_width == -1:
                computed_width = default_width
            if computed_height == -1:
                computed_height = default_height

        return (computed_width, computed_height)

    def _compute_minimum_size(self):
        """ Computes and returns the minimum size of the window.

        """
        # If the user has supplied an explicit minimum size, use that.
        computed_width, computed_height = self.minimum_size
        if computed_width != -1 and computed_height != -1:
            return (computed_width, computed_height)
        
        # Otherwise, try to compute a default from the central widget.
        widget = self.central_widget
        if widget is not None:

            # If the central widget is a container, we have it compute
            # the minimum size for us, otherwise, we use the size hint
            # of the widget as the value.
            if isinstance(widget, Container):
                min_width, min_height = widget.compute_min_size()
            else:
                min_width, min_height = widget.size_hint()

            # If the hug and resist clip policies of the widget are
            # weaker than the resize strength of the window, then
            # we ignore its value in that direction.
            if ((widget.hug_width not in STRONGER_THAN_RESIZE) and
                (widget.resist_clip_width not in STRONGER_THAN_RESIZE)):
                min_width = -1
            
            if ((widget.hug_height not in STRONGER_THAN_RESIZE) and
                (widget.resist_clip_height not in STRONGER_THAN_RESIZE)):
                min_height = -1 

            if computed_width == -1:
                computed_width = min_width

            if computed_height == -1:
                computed_height = min_height
        
        # We use the last resort values to replace any remaining 
        # -1 values. This ensures the return value will be >= 0 
        # in both width and height
        if computed_width == -1 or computed_height == -1:
            default_width, default_height = self.minimum_size_default
            if computed_width == -1:
                computed_width = default_width
            if computed_height == -1:
                computed_height = default_height
        
        return (computed_width, computed_height)

    def _compute_maximum_size(self):
        """ Computes and returns the maximum size of the window.

        """
        # If the user has supplied an explicit maximum size, use that.
        computed_width, computed_height = self.maximum_size
        if computed_width != -1 and computed_height != -1:
            return (computed_width, computed_height)
        
        # Otherwise, try to compute a default from the central widget.
        widget = self.central_widget
        if widget is not None:

            # If the central widget is a container, we have it compute
            # the maximum size for us, otherwise, we use the size hint
            # of the widget as the value.
            if isinstance(widget, Container):
                max_width, max_height = widget.compute_max_size()
            else:
                max_width, max_height = widget.size_hint()

            # If the hug policy of the widget is weaker than the 
            # resize strength of the window, then we ignore its 
            # value in that direction.
            if widget.hug_width not in STRONGER_THAN_RESIZE:
                max_width = -1
            
            if widget.hug_height not in STRONGER_THAN_RESIZE:
                max_height = -1 

            if computed_width == -1:
                computed_width = max_width

            if computed_height == -1:
                computed_height = max_height
        
        # We use the last resort values to replace any remaining 
        # -1 values. This ensures the return value will be >= 0 
        # in both width and height.
        if computed_width == -1 or computed_height == -1:
            default_width, default_height = self.maximum_size_default
            if computed_width == -1:
                computed_width = default_width
            if computed_height == -1:
                computed_height = default_height
        
        return (computed_width, computed_height)

