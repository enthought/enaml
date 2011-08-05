from enthought.traits.api import Any, Bool, Enum, Event, Int, Property, Tuple

from ..constants import Color, Layout, SizePolicy
from ..registry import register_element
from .abstract_item import AbstractItem


@register_element
class Element(AbstractItem):
    
    # The bgcolor of the widget
    bgcolor = Tuple(Color.DEFAULT)

    # Whether the widget is enabled
    enabled = Bool(True)
    
    # The font object assigned to the widget
    #font = Any # XXX should be Instance(Font)
    
    # The height of the widget. Synced with size.
    height = Int(-1)
    
    # The layout direction of the children
    layout = Enum(Layout.DEFAULT, *Layout.values())

    # The (x, y) position of the widget in its parent
    # We sync this with width and height, but need some 
    # special flags and event to prevent duplicate trait
    # notification issues.
    pos = Property(depends_on='_pos_evt')
    _setting_pos = Bool(False)
    _pos_evt = Event

    # The (width, height) size of the widget
    # We sync this with x and y, but need some 
    # special flags and event to prevent duplicate 
    # trait notification issues.
    size = Property(depends_on='_size_evt')
    _setting_size = Bool(False)
    _size_evt = Event
    
    # The size hint for the wiget. (-1, -1) is the default.
    size_hint = Tuple((-1, -1))
    
    # The size policy for the widget, used in conjunction 
    # with size_hint to determine the size of a widget in its
    # parent layout.
    size_policy = Tuple(Enum(SizePolicy.DEFAULT, *SizePolicy.values()),
                        Enum(SizePolicy.DEFAULT, *SizePolicy.values()))

    # Whether the widget is visible
    visible = Bool(True)

    # The width of the widget. Synced with size.
    width = Int(-1)

    # The X position of the widget in its parent. Synced with pos.
    x = Int(-1)

    # The Y position of the widget in its parent. Synced with pos.
    y = Int(-1)
    
    #--------------------------------------------------------------------------
    # Property Handlers
    #--------------------------------------------------------------------------
    
    # This arrangment of handlers *mostly* prevents duplicate notifications
    # A few will slip through depending on the way in which the pos 
    # or size traits are changed. The _setting_* flags are required
    # to prevent the widget from jumping when being moved.

    def _get_size(self):
        return (self.width, self.height)
    
    def _set_size(self, size):
        self._setting_size = True
        self.width, self.height = size
        self._setting_size = False
        self._size_evt = True

    def _width_changed(self):
        if not self._setting_size:
            self._size_evt = True

    def _height_changed(self):
        if not self._setting_size:
            self._size_evt = True

    def _get_pos(self):
        return (self.x, self.y)
    
    def _set_pos(self, pos):
        self._setting_pos = True
        self.x, self.y = pos
        self._setting_pos = False
        self._pos_evt = True

    def _x_changed(self):
        if not self._setting_pos:
            self._pos_evt = True

    def _y_changed(self):
        if not self._setting_pos:
            self._pos_evt = True


