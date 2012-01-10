#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import (
    List, Instance, Property, Tuple, Event, Enum, cached_property,
)

from .component import Component, AbstractTkComponent
from .layout.box_model import BoxModel

from ..guard import guard


PolicyEnum = Enum('ignore', 'weak', 'medium', 'strong', 'required')


#------------------------------------------------------------------------------
# Abstract Toolkit Layout Component Interface
#------------------------------------------------------------------------------
class AbstractTkLayoutComponent(AbstractTkComponent):
    """ The abstract toolkit LayoutComponent interface.

    A toolkit layout component is responsible for handling changes on 
    a shell LayoutComponent and proxying those changes to and from its 
    internal toolkit widget.

    """
    @abstractmethod
    def size(self):
        """ Returns the size of the internal toolkit widget, ignoring any
        windowing decorations, as a (width, height) tuple of integers.

        """
        raise NotImplementedError
    
    @abstractmethod
    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state, ignoring
        any windowing decorations. This value is used by the layout 
        manager to determine how much space to allocate the widget.

        """
        raise NotImplementedError

    @abstractmethod
    def resize(self, width, height):
        """ Resizes the internal toolkit widget according the given
        width and height integers, ignoring any windowing decorations.

        """
        raise NotImplementedError
    
    @abstractmethod
    def min_size(self):
        """ Returns the hard minimum (width, height) of the widget, 
        ignoring any windowing decorations. A widget will not be able
        to be resized smaller than this value

        """
        raise NotImplementedError

    @abstractmethod
    def set_min_size(self, min_width, min_height):
        """ Set the hard minimum width and height of the widget, ignoring
        any windowing decorations. A widget will not be able to be resized 
        smaller than this value.

        """
        raise NotImplementedError

    @abstractmethod
    def pos(self):
        """ Returns the position of the internal toolkit widget as an
        (x, y) tuple of integers, including any windowing decorations. 
        The coordinates should be relative to the origin of the widget's 
        parent, or to the screen if the widget is toplevel.

        """
        raise NotImplementedError
    
    @abstractmethod
    def move(self, x, y):
        """ Moves the internal toolkit widget according to the given
        x and y integers which are relative to the origin of the
        widget's parent and includes any windowing decorations.

        """
        raise NotImplementedError
        
    @abstractmethod
    def frame_geometry(self):
        """ Returns an (x, y, width, height) tuple of geometry info
        for the internal toolkit widget, including any windowing
        decorations.

        """
        raise NotImplementedError

    @abstractmethod
    def geometry(self):
        """ Returns an (x, y, width, height) tuple of geometry info
        for the internal toolkit widget, ignoring any windowing
        decorations.

        """
        raise NotImplementedError
    
    @abstractmethod
    def set_geometry(self, x, y, width, height):
        """ Sets the geometry of the internal widget to the given
        x, y, width, and height values, ignoring any windowing 
        decorations.

        """
        raise NotImplementedError

    def set_solved_geometry(self, root):
        """ Makes the component take the solved geometry and other 
        constrained variables and set its internal values.

        This method can assume that all of its parents have had their 
        geometry set correctly.

        Parameters
        ----------
        root : Container
            The root container that actually performed the layout for 
            this component. Implementations will need this to know how 
            to transform the global solved (x,y) values to local values 
            relative to their immediate parent.

        Returns
        -------
        dx, dy : int
            The offsets needed to convert (x, y) variable values into 
            local positions. These are mostly used in overrides of this 
            method that handle additional variables.

        """
        shell = self.shell_obj
        x = shell.left.value
        y = shell.top.value
        width = shell.width.value
        height = shell.height.value
        x, y, width, height = (int(round(z)) for z in (x, y, width, height))
        # This is offset against the root Container. Each Component's 
        # geometry actually needs to be offset against its parent. Walk 
        # up the tree and subtract out the parent's offset.
        dx = 0
        dy = 0
        for ancestor in shell.traverse_ancestors(root):
            adx, ady, _, _ = ancestor.geometry()
            dx += adx
            dy += ady
        self.set_geometry(x - dx, y - dy, width, height)
        return (dx, dy)


#------------------------------------------------------------------------------
# Enaml Layout Component
#------------------------------------------------------------------------------
class LayoutComponent(Component):
    """ A Component subclass that adds a box model and support for 
    constraints specification. This class represents the most basic
    widget in Enaml that can partake in constraints-base layout.

    """
    #: The list of children that can participate in constraints based
    #: layout. This list is composed of components in the list of 
    #: children that are instances of LayoutComponent.
    layout_children = Property(List, depends_on='children')

    #: A private attribute that holds the box model instance
    #: for this component. 
    _box_model = Instance(BoxModel)
    def __box_model_default(self):
        return BoxModel(self)

    #: How strongly a component hugs it's contents' width. Valid strengths
    #: are 'weak', 'medium', 'strong', 'required' and 'ignore'. Default is 
    #: 'strong'. This trait should be overridden on a per-control basis to
    #: specify a logical default for the given control.
    hug_width = PolicyEnum('strong')

    #: How strongly a component hugs it's contents' height. Valid strengths
    #: are 'weak', 'medium', 'strong', 'required' and 'ignore'. Default is
    #: 'strong'. This trait should be overridden on a per-control basis to 
    #: specify a logical default for the given control.
    hug_height = PolicyEnum('strong')

    #: The combination of (hug_width, hug_height).
    hug = Property(
        Tuple(PolicyEnum, PolicyEnum), depends_on=['hug_width', 'hug_height'],
    )

    #: How strongly a component resists clipping its contents. Valid 
    #: strengths are 'weak', 'medium', 'strong', 'required' and 'ignore'. 
    #: The default is 'strong' for width.
    resist_clip_width = PolicyEnum('strong')

    #: How strongly a component resists clipping its contents. Valid 
    #: strengths are 'weak', 'medium', 'strong', 'required' and 'ignore'. 
    #: The default is 'strong' for height.
    resist_clip_height = PolicyEnum('strong')

    #: The combination of (resist_clip_width, resist_clip_height).
    resist_clip = Property(
        Tuple(PolicyEnum, PolicyEnum),
        depends_on=['resist_clip_width', 'resist_clip_height'],
    )

    #: An event that should be emitted by the abstract obj when its size 
    #: hint has updated due to some change.
    size_hint_updated = Event

    #: A read-only symbolic object that represents the left boundary of 
    #: the component
    left = Property

    #: A read-only symbolic object that represents the top boundary of 
    #: the component
    top = Property

    #: A read-only symbolic object that represents the width of the 
    #: component
    width = Property

    #: A read-only symbolic object that represents the height of the 
    #: component
    height = Property

    #: A read-only symbolic object that represents the right boundary 
    #: of the component
    right = Property

    #: A read-only symbolic object that represents the bottom boundary 
    #: of the component
    bottom = Property

    #: A read-only symbolic object that represents the vertical center 
    #: of the component
    v_center = Property

    #: A read-only symbolic object that represents the horizontal 
    #: center of the component
    h_center = Property

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkLayoutComponent)

    #--------------------------------------------------------------------------
    # Property Getters and Setters
    #--------------------------------------------------------------------------
    @cached_property
    def _get_layout_children(self):
        """ Cached property getter for the 'layout_children' property. 
        This getter returns the sublist of children that are instances 
        of LayoutComponent.

        """
        flt = lambda child: isinstance(child, LayoutComponent)
        return filter(flt, self.children)

    def _get_left(self):
        """ Property getter for the 'left' property.

        """
        return self._box_model.left
    
    def _get_top(self):
        """ Property getter for the 'top' property.

        """
        return self._box_model.top
    
    def _get_width(self):
        """ Property getter for the 'width' property.

        """
        return self._box_model.width
    
    def _get_height(self):
        """ Property getter for the 'height' property.

        """
        return self._box_model.height
    
    def _get_right(self):
        """ Property getter for the 'right' property.

        """
        return self._box_model.right
    
    def _get_bottom(self):
        """ Property getter for the 'bottom' property.

        """
        return self._box_model.bottom
    
    def _get_v_center(self):
        """ Property getter for the 'v_center' property.

        """
        return self._box_model.v_center
    
    def _get_h_center(self):
        """ Property getter for the 'h_center' property.

        """
        return self._box_model.h_center

    def _get_hug(self):
        """ Property getter for the 'hug' property.

        """
        return (self.hug_width, self.hug_height)

    def _set_hug(self, value):
        """ Property setter for the 'hug' property.

        """
        width, height = value
        self.trait_set(hug_width=width, hug_height=height)

    def _get_resist_clip(self):
        """ Property getter for the 'resist_clip' property.

        """
        return (self.resist_clip_width, self.resist_clip_height)

    def _set_resist_clip(self, value):
        """ Property setter for the 'resist_clip' property.

        """
        width, height = value
        self.trait_set(resist_clip_width=width, resist_clip_height=height)

    #--------------------------------------------------------------------------
    # Setup Methods 
    #--------------------------------------------------------------------------
    def _setup_init_layout(self):
        """ A reimplemented parent class setup method that performs any
        layout initialization necessary for the component. The layout
        is initialized from the bottom up.

        """
        super(LayoutComponent, self)._setup_init_layout()
        self.initialize_layout()

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def _layout_children_changed(self):
        """ Handles the layout children being changed on this component 
        by enqueing a request for relayout so long as this component has
        been fully initialized.

        """
        if self.initialized:
            # We only need to make sure things get a relayout. We can 
            # do this by simply enqueuing an empty callable. This makes
            # sure we don't trigger multiple relayouts if some other
            # part of the framework has requested the same.
            self.relayout_enqueue(lambda: None)
    
    #--------------------------------------------------------------------------
    # Auxiliary Methods
    #--------------------------------------------------------------------------
    def initialize_layout(self):
        """ A method that is called when the layout of this component
        should be initialized. By default, this is a no-op. Subclasses
        should reimplement this method as necessary to initialize any
        required layouts.

        """
        pass
        
    def set_visible(self, visible):
        """ Set the visibility of the component according to the given
        boolean. This is a reimplemented parent class method that makes
        sure the appropriate relayout requests are made since a component
        that is not visible does not participate in constraints-based
        layout.

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

        if self.initialized:
            if self.parent is None:
                # If the component is initialized and it is a toplevel
                # component, then it is safe to set the visibility
                # immediately. 
                #
                # XXX we need to pump the event loop a couple of times 
                # to get things to initialize properly. It would be good
                # to not have to do this.
                self.toolkit.process_events()
                self.toolkit.process_events()
                self.abstract_obj.set_visible(visible)
            else:
                # If the component is initialized but it is not toplevel,
                # then the visibility change must occur in a deferred
                # context, since changing the visibility of a nested
                # component will require a layout update.
                def visibility_closure():
                    self.abstract_obj.set_visible(visible)
                self.relayout_enqueue(visibility_closure)
        else:
            # If the component is not yet initialized, and it is not a 
            # toplevel component, then it is safe to set the visibility
            # immediately since a visible child of a non-visible parent 
            # will remain hidden until its parent is shown. For toplevel
            # components which are uninitialized, this method is a no-op 
            # since it would not yet be safe to display the widget.
            if self.parent is not None:
                self.abstract_obj.set_visible(visible)

    def size(self):
        """ Returns the size tuple as given by the abstract widget.

        """
        return self.abstract_obj.size()
    
    def size_hint(self):
        """ Returns the size hint tuple as given by the abstract widget
        for its current state.

        """
        return self.abstract_obj.size_hint()

    def resize(self, width, height):
        """ Resize the abstract widget as specified by the given
        width and height integers.

        """
        self.abstract_obj.resize(width, height)
    
    def min_size(self):
        """ Returns the hard minimum (width, height) of the widget, 
        ignoring any windowing decorations. A widget will not be able
        to be resized smaller than this value

        """
        return self.abstract_obj.min_size()

    def set_min_size(self, min_width, min_height):
        """ Set the hard minimum width and height of the widget. A widget
        should not be able to be resized smaller than this value.

        """
        self.abstract_obj.set_min_size(min_width, min_height)

    def pos(self):
        """ Returns the position tuple as given by the abstract widget.

        """
        return self.abstract_obj.pos()
    
    def move(self, x, y):
        """ Moves the abstract widget to the given x and y integer
        coordinates which are given relative to the parent origin.

        """
        self.abstract_obj.move(x, y)
    
    def geometry(self):
        """ Returns the (x, y, width, height) geometry tuple as given
        by the abstract widget.

        """
        return self.abstract_obj.geometry()
    
    def set_geometry(self, x, y, width, height):
        """ Sets the geometry of the abstract widget with the given
        integer values.

        """
        self.abstract_obj.set_geometry(x, y, width, height)

    def set_solved_geometry(self, root):
        """ Makes the component take the solved geometry and other 
        constrained variables and set its internal values.

        This method can assume that all of its parents have had their 
        geometry set correctly.

        """
        return self.abstract_obj.set_solved_geometry(root)

