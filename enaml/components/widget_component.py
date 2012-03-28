#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance, Property, Bool

from .base_widget_component import (
    BaseWidgetComponent, AbstractTkBaseWidgetComponent,
)

from ..core.trait_types import EnamlEvent
from ..guard import guard
from ..styling.color import ColorTrait
from ..styling.font import FontTrait


#------------------------------------------------------------------------------
# Freeze Context
#------------------------------------------------------------------------------
class FreezeContext(object):
    """ A context manager which disables rendering updates of a component
    on enter, and re-enables them on exit. It may safely nested.

    """
    _counts = {}

    @classmethod
    def is_frozen(cls, component):
        """ Returns a boolean indicating whether or not the given 
        component is currently the subject of a freeze context.

        """
        return component in cls._counts

    def __init__(self, component):
        """ Initialize a freeze context.

        Parameters
        ----------
        component : BaseComponent
            The component that should be frozen.
        
        """
        self.component = component
    
    def __enter__(self):
        """ Disables updates on the component the first time that any
        freeze context on that component is entered.

        """
        counts = self._counts
        cmpnt = self.component
        if cmpnt not in counts:
            counts[cmpnt] = 1
            cmpnt.disable_updates()
        else:
            counts[cmpnt] += 1
    
    def __exit__(self, exc_type, exc_value, traceback):
        """ Enables updates on the component when the last freeze
        context on that component is exited.

        """
        counts = self._counts
        cmpnt = self.component
        counts[cmpnt] -= 1
        if counts[cmpnt] == 0:
            del counts[cmpnt]
            cmpnt.enable_updates()


#------------------------------------------------------------------------------
# Abstract Toolkit Widget Component Interface
#------------------------------------------------------------------------------
class AbstractTkWidgetComponent(AbstractTkBaseWidgetComponent):
    """ The abstract toolkit WidgetComponent interface.

    This abstract interface adds support for widgets that can paint on
    the screen, and thus have associated geometry and style information.

    """
    @abstractmethod
    def disable_updates(self):
        """ Called when the widget should disable its rendering updates.

        This is used before a large change occurs to a live ui so that
        the widget can optimize/delay redrawing until all the updates
        have been completed and 'enable_updates' is called.

        """
        raise NotImplementedError

    @abstractmethod
    def enable_updates(self):
        """ Called when the widget should enable rendering updates.

        This is used in conjunction with 'disable_updates' to allow
        a widget to optimize/delay redrawing until all the updates
        have been completed and this function is called.

        """
        raise NotImplementedError

    @abstractmethod
    def set_visible(self, visible):
        """ Set the visibility of the of the widget according to the
        given boolean.

        """
        raise NotImplementedError

    @abstractmethod
    def size_hint(self):
        """ Returns the size hint Size tuple as given by the abstract 
        widget for its current state.

        """
        raise NotImplementedError

    @abstractmethod
    def layout_geometry(self):
        """ Returns the Rect tuple of layout geometry info as given by 
        the abstract object. It may be different from the value returned 
        by geometry() if the widget's effective layout rect is different 
        from its paintable rect.

        """
        raise NotImplementedError

    @abstractmethod
    def set_layout_geometry(self, rect):
        """ Sets the layout geometry of the internal widget to the 
        given Rect.

        """
        raise NotImplementedError

    @abstractmethod
    def geometry(self):
        """ Returns the Rect geometry tuple as given by the abstract 
        widget.

        """
        raise NotImplementedError
    
    @abstractmethod
    def set_geometry(self, rect):
        """ Sets the geometry of the abstract widget with the given
        Rect.

        """
        raise NotImplementedError

    @abstractmethod
    def min_size(self):
        """ Returns the hard minimum Size of the widget, ignoring any 
        windowing decorations. A widget will not be able to be resized
        smaller than this value

        """
        raise NotImplementedError

    @abstractmethod
    def set_min_size(self, size):
        """ Set the hard minimum Size of the widget, ignoring any 
        windowing decorations. A window will not be able to be resized 
        smaller than this value.

        """
        raise NotImplementedError

    @abstractmethod
    def max_size(self):
        """ Returns the hard maximum Size of the widget, ignoring any
        windowing decorations. A widget will not be able to be resized
        larger than this value

        """
        raise NotImplementedError

    @abstractmethod
    def set_max_size(self, size):
        """ Set the hard maximum Size of the widget, ignoring any 
        windowing decorations. A widget will not be able to be resized 
        larger than this value.

        """
        raise NotImplementedError

    @abstractmethod
    def size(self):
        """ Returns the Size as given by the abstract widget.

        """
        raise NotImplementedError
        
    @abstractmethod
    def resize(self, size):
        """ Resize the abstract widget as specified by the given Size.

        """
        raise NotImplementedError

    @abstractmethod
    def pos(self):
        """ Returns the Pos tuple as given by the abstract widget.

        """
        raise NotImplementedError
    
    @abstractmethod
    def move(self, pos):
        """ Moves the abstract widget to the given Pos position relative
        to the its parent's origin

        """
        raise NotImplementedError

    @abstractmethod
    def shell_enabled_changed(self, enabled):
        """ The change handler for the 'enabled' attribute of the shell
        object. Sets the widget enabled according to the given boolean.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_bgcolor_changed(self, color):
        """ The change handler for the 'bgcolor' attribute on the shell
        object. Sets the background color of the internal widget to the 
        given color.
        
        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_fgcolor_changed(self, color):
        """ The change handler for the 'fgcolor' attribute on the shell
        object. Sets the foreground color of the internal widget to the 
        given color. For some widgets this may do nothing.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_font_changed(self, font):
        """ The change handler for the 'font' attribute on the shell
        object. Sets the font of the internal widget to the given font.
        For some widgets this may do nothing.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Widget Component
#------------------------------------------------------------------------------
class WidgetComponent(BaseWidgetComponent):
    """ A BaseWidgetComponent subclass that adds support for a visual
    toolkit widget information.

    """
    #: Whether or not the widget is enabled.
    enabled = Bool(True)

    #: Whether or not the widget is visible.
    visible = Bool(True)

    #: The background color of the widget.
    bgcolor = ColorTrait

    #: The foreground color of the widget.
    fgcolor = ColorTrait

    #: The font used for the widget.
    font = FontTrait

    #: A property which returns whether or not this component is 
    #: currently frozen.
    frozen = Property

    #: An event that should be emitted when the size hint been updated.
    size_hint_updated = EnamlEvent

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkWidgetComponent) 

    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    def _get_frozen(self):
        """ The property getter for the 'frozen' attribute.

        """
        return FreezeContext.is_frozen(self)

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def _setup_init_visibility(self):
        """ A reimplemented parent class setup method which initializes
        the visibility of the component.

        """
        self.set_visible(self.visible)
        super(WidgetComponent, self)._setup_init_visibility()
    
    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def _visible_changed(self, visible):
        """ Handles the 'visible' attribute being changed by calling the
        'set_visible' method and requesting the parent.

        """
        # The method call allows the visibility to be set by other parts 
        # of the framework which are not dependent on change notification.
        # By using the method here, we help to ensure a consistent state.
        self.set_visible(visible)

    def _size_hint_updated_changed(self):
        """ A change handler which requests a relayout from its *parent*
        when its size hint has updated, provided that the component is
        initialized.

        Note that it is critical that the request be made to the parent,
        since a given component has no use for its size hint in its 
        internal layout computations.

        """
        if self.initialized:
            parent = self.parent
            if parent is not None:
                parent.request_relayout()

    #--------------------------------------------------------------------------
    # Geometry Methods
    #--------------------------------------------------------------------------
    def size_hint(self):
        """ Returns the size hint Size tuple as given by the abstract 
        widget for its current state.

        """
        return self.abstract_obj.size_hint()

    def layout_geometry(self):
        """ Returns the Rect tuple of layout geometry info as given by 
        the abstract object. It may be different from the value returned 
        by geometry() if the widget's effective layout rect is different 
        from its paintable rect.

        """
        return self.abstract_obj.layout_geometry()

    def set_layout_geometry(self, rect):
        """ Sets the layout geometry of the internal widget to the 
        given Rect.

        """
        self.abstract_obj.set_layout_geometry(rect)

    def geometry(self):
        """ Returns the Rect geometry tuple as given by the abstract 
        widget.

        """
        return self.abstract_obj.geometry()
    
    def set_geometry(self, rect):
        """ Sets the geometry of the abstract widget with the given
        Rect.

        """
        self.abstract_obj.set_geometry(rect)

    def min_size(self):
        """ Returns the hard minimum Size of the widget, ignoring any 
        windowing decorations. A widget will not be able to be resized
        smaller than this value

        """
        return self.abstract_obj.min_size()

    def set_min_size(self, size):
        """ Set the hard minimum Size of the widget, ignoring any 
        windowing decorations. A window will not be able to be resized 
        smaller than this value.

        """
        self.abstract_obj.set_min_size(size)

    def max_size(self):
        """ Returns the hard maximum Size of the widget, ignoring any
        windowing decorations. A widget will not be able to be resized
        larger than this value

        """
        return self.abstract_obj.max_size()

    def set_max_size(self, size):
        """ Set the hard maximum Size of the widget, ignoring any 
        windowing decorations. A widget will not be able to be resized 
        larger than this value.

        """
        self.abstract_obj.set_max_size(size)

    def size(self):
        """ Returns the Size as given by the abstract widget.

        """
        return self.abstract_obj.size()

    def resize(self, size):
        """ Resize the abstract widget as specified by the given Size.

        """
        self.abstract_obj.resize(size)

    def pos(self):
        """ Returns the Pos tuple as given by the abstract widget.

        """
        return self.abstract_obj.pos()
    
    def move(self, pos):
        """ Moves the abstract widget to the given Pos position relative
        to the its parent's origin

        """
        self.abstract_obj.move(pos)
    
    #--------------------------------------------------------------------------
    # Auxiliary Methods 
    #--------------------------------------------------------------------------
    def set_visible(self, visible):
        """ Set the visibility of the component according to the given
        boolean. Subclasses that need more control over visibility
        changes should reimplement this method.

        """
        # Make sure the 'visible' attribute is synced up as a result
        # of the method call. This may fire a notification, in which
        # case the change handler will call this method again. This
        # guard prevents that unneeded recursion.
        if guard.guarded(self, 'set_visible'):
            return
        else:
            with guard(self, 'set_visible'):
                self.visible = visible
        
        # Only set the visibility of the component if it is fully 
        # initialized or being set to False. This prevents situations 
        # where a widget is shown prematurely in some toolkit backends
        # which then causes the entire window hierarchy to be shown
        # prematurely.
        #
        # XXX this is still a bit gorpy and needs some work.
        if self.initialized:
            self.request_relayout_task(self.abstract_obj.set_visible, visible)
        elif not visible or self.parent is not None:
            self.abstract_obj.set_visible(visible)

    def disable_updates(self):
        """ Disables rendering updates for the underlying widget.

        """
        self.abstract_obj.disable_updates()

    def enable_updates(self):
        """ Enables rendering updates for the underlying widget.

        """
        self.abstract_obj.enable_updates()

    def freeze(self):
        """ A context manager which disables rendering updates on 
        enter and restores them on exit. The context can be safetly
        nested.

        """
        return FreezeContext(self)

