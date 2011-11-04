#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod, abstractproperty

from traits.api import Instance, Property, Tuple, Event, Enum

from .base_component import BaseComponent, AbstractTkBaseComponent
from ..styling.color import ColorTrait
from ..styling.font import FontTrait
from .layout.box_model import BoxModel

PolicyEnum = Enum('ignore', 'weak', 'medium', 'strong', 'required')

class AbstractTkComponent(AbstractTkBaseComponent):
    """ The abstract toolkit Component interface.

    A toolkit component is responsible for handling changes on a shell 
    Component and proxying those changes to and from its internal toolkit
    widget.

    """
    @abstractproperty
    def toolkit_widget(self):
        """ An abstract property that should return the gui toolkit 
        widget being managed by the object.

        """
        raise NotImplementedError

    @abstractmethod
    def size(self):
        """ Return the size of the internal toolkit widget as a 
        (width, height) tuple of integers.

        """
        raise NotImplementedError
    
    @abstractmethod
    def size_hint(self):
        """ Returns a (width, height) tuple of integers which represent
        the suggested size of the widget for its current state. This 
        value is used by the layout manager to determine how much 
        space to allocate the widget.

        """
        raise NotImplementedError

    @abstractmethod
    def resize(self, width, height):
        """ Resizes the internal toolkit widget according the given
        width and height integers.

        """
        raise NotImplementedError
    
    @abstractmethod
    def set_min_size(self, min_width, min_height):
        """ Set the hard minimum width and height of the widget. A widget
        should not be able to be resized smaller than this value.

        """
        raise NotImplementedError

    @abstractmethod
    def pos(self):
        """ Returns the position of the internal toolkit widget as an 
        (x, y) tuple of integers. The coordinates should be relative to
        the origin of the widget's parent.

        """
        raise NotImplementedError
    
    @abstractmethod
    def move(self, x, y):
        """ Moves the internal toolkit widget according to the given
        x and y integers which are relative to the origin of the
        widget's parent.

        """
        raise NotImplementedError
    
    @abstractmethod
    def geometry(self):
        """ Returns an (x, y, width, height) tuple of geometry info
        for the internal toolkit widget. The semantic meaning of the
        values are the same as for the 'size' and 'pos' methods.

        """
        raise NotImplementedError
    
    @abstractmethod
    def set_geometry(self, x, y, width, height):
        """ Sets the geometry of the internal widget to the given 
        x, y, width, and height values. The semantic meaning of the
        values is the same as for the 'resize' and 'move' methods.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_bg_color_changed(self, color):
        """ The change handler for the 'bg_color' attribute on the parent.
        Sets the background color of the internal widget to the given color.
        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_fg_color_changed(self, color):
        """ The change handler for the 'fg_color' attribute on the parent.
        Sets the foreground color of the internal widget to the given color.
        For some widgets this may do nothing.
        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_font_changed(self, font):
        """ The change handler for the 'font' attribute on the parent.
        Sets the font of the internal widget to the given font.
        For some widgets this may do nothing.
        """
        raise NotImplementedError

class Component(BaseComponent):
    """ A BaseComponent subclass that adds a box model and support
    for constraints specification. This class represents the most
    basic visible widget in Enaml.

    """
    #: A private attribute that holds the box model instance
    #: for this component. 
    _box_model = Instance(BoxModel, ())

    #: How strongly a component hugs it's contents' width. Valid strengths
    #: are 'weak', 'medium', 'strong', 'required' and 'ignore'. 
    #: The default is 'strong'. This trait should be overridden on a per-control
    #: basis to specify  a logical default for the given control.
    hug_width = PolicyEnum('strong')

    #: How strongly a component hugs it's contents' height. Valid strengths
    #: are 'weak', 'medium', 'strong', 'required' and 'ignore'. 
    #: The default is 'strong'. This trait should be overridden on a per-control
    #: basis to specify  a logical default for the given control.
    hug_height = PolicyEnum('strong')

    #: The combination of (hug_width, hug_height).
    hug = Property(Tuple(PolicyEnum, PolicyEnum), depends_on=['hug_width', 'hug_height'])

    #: How strongly a component resists clipping its contents. 
    #: Valid strengths are 'weak', 'medium', 'strong', 'required'
    #: and 'ignore'. The default is 'strong' for width.
    resist_clip_width = PolicyEnum('strong')

    #: How strongly a component resists clipping its contents. 
    #: Valid strengths are 'weak', 'medium', 'strong', 'required'
    #: and 'ignore'. The default is 'strong' for height.
    resist_clip_height = PolicyEnum('strong')

    #: The combination of (resist_clip_width, resist_clip_height).
    resist_clip = Property(Tuple(PolicyEnum, PolicyEnum), depends_on=['resist_clip_width', 'resist_clip_height'])

    #: An event that should be emitted by the abstract obj when
    #: its size hint has updated do to some change.
    size_hint_updated = Event

    #: A read-only symbolic object that represents the left 
    #: boundary of the component
    left = Property

    #: A read-only symbolic object that represents the top 
    #: boundary of the component
    top = Property

    #: A read-only symbolic object that represents the width
    #: of the component
    width = Property

    #: A read-only symbolic object that represents the height 
    #: of the component
    height = Property

    #: A read-only symbolic object that represents the right 
    #: boundary of the component
    right = Property

    #: A read-only symbolic object that represents the bottom 
    #: boundary of the component
    bottom = Property

    #: A read-only symbolic object that represents the vertical 
    #: center of the component
    v_center = Property

    #: A read-only symbolic object that represents the horizontal 
    #: center of the component
    h_center = Property
    
    #: The background colour of the widget
    bg_color = Property(ColorTrait, depends_on=['_user_bg_color', '_style_bg_color'])
    
    #: Private trait holding the user-set background color value
    _user_bg_color = ColorTrait
    
    #: Private trait holding the background color value from the style
    _style_bg_color = ColorTrait

    #: The foreground colour of the widget
    fg_color = Property(ColorTrait, depends_on=['_user_fg_color', '_style_fg_color'])
    
    #: Private trait holding the user-set foreground color value
    _user_fg_color = ColorTrait
    
    #: Private trait holding the foreground color value from the style
    _style_fg_color = ColorTrait

    #: The foreground colour of the widget
    font = Property(FontTrait, depends_on=['_user_font', '_style_font'])
    
    #: Private trait holding the user-set foreground color value
    _user_font = FontTrait
    
    #: Private trait holding the foreground color value from the style
    _style_font = FontTrait

    #: The background colour can be set by the style system
    _style_tags = ('bg_color', 'fg_color')

    #: A read-only property that returns the toolkit specific widget
    #: being managed by the abstract widget.
    toolkit_widget = Property

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkComponent)

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
        self.trait_set(
            hug_width=value[0],
            hug_height=value[1],
        )

    def _get_resist_clip(self):
        """ Property getter for the 'resist_clip' property.

        """
        return (self.resist_clip_width, self.resist_clip_height)

    def _set_resist_clip(self, value):
        """ Property setter for the 'resist_clip' property.

        """
        self.trait_set(
            resist_clip_width=value[0],
            resist_clip_height=value[1],
        )

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

    def _set_bg_color(self, new):
        """ Property setter for the 'bg_color' background color property.
        Set values are pushed to the '_user_bg_color' trait.
        """
        self._user_bg_color = new
    
    def _get_bg_color(self):
        """ Property sgtter for the 'bg_color' background color property.
        We use the '_user_bg_color' trait unless it is None.
        """
        if self._user_bg_color:
            return self._user_bg_color
        return self._style_bg_color

    def _set_fg_color(self, new):
        """ Property setter for the 'fg_color' foreground color property.
        Set values are pushed to the '_user_fg_color' trait.
        """
        self._user_fg_color = new
    
    def _get_fg_color(self):
        """ Property sgtter for the 'fg_color' foreground color property.
        We use the '_user_fg_color' trait unless it is None.
        """
        if self._user_fg_color:
            return self._user_fg_color
        return self._style_fg_color

    def _set_font(self, new):
        """ Property setter for the 'fg_color' foreground color property.
        Set values are pushed to the '_user_fg_color' trait.
        """
        self._user_font = new
    
    def _get_font(self):
        """ Property sgtter for the 'fg_color' foreground color property.
        We use the '_user_fg_color' trait unless it is None.
        """
        if self._user_font:
            return self._user_font
        return self._style_font

    def _get_toolkit_widget(self):
        """ Property getter for the 'toolkit_widget' property.

        """
        return self.abstract_obj.toolkit_widget

