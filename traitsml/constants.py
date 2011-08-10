""" The Constants used throughout TraitsML. """


#------------------------------------------------------------------------------
# Constant class support.
#------------------------------------------------------------------------------
class Constant(object):

    __slots__ = ('cls_name', 'name')

    def __repr__(self):
        return '%s.%s' % (self.cls_name, self.name)

    def __str__(self):
        return repr(self)


class ConstantContainerMeta(type):
    # Any class attribute of a subclass of Constant that is all 
    # uppercase is assumed to be a constant
   
    def __new__(meta, cls_name, bases, cls_dict):
        values = []
        for key, value in cls_dict.iteritems():
            if key.isupper():
                values.append(value)
                if isinstance(value, Constant):
                    value.cls_name = cls_name
                    value.name = key
        cls_dict['__values__'] = tuple(values)
        return type.__new__(meta, cls_name, bases, cls_dict)

    def __call__(cls, *args, **kwargs):
        raise RuntimeError('Cannot instantiate a ConstantContainer.')
    
    def __setattr__(cls, name, val):
        raise AttributeError('Cannot change the value of a Constant.')


class ConstantContainer(object):
    
    __metaclass__ = ConstantContainerMeta

    @classmethod
    def values(cls):
        return cls.__values__


#------------------------------------------------------------------------------
# Implemented Constants
#------------------------------------------------------------------------------
class Align(ConstantContainer):
   
    # The default toolkit alignment
    DEFAULT = Constant()

    # Align with the left edge
    LEFT = Constant()

    # Align with the right edge
    RIGHT = Constant()

    # Center horizontally
    HCENTER = Constant()

    # Justify in the available space
    JUSTIFY = Constant()

    # Align with the top
    TOP = Constant()

    # Align with the bottom
    BOTTOM = Constant()

    # Center vertically
    VCENTER = Constant()

    # Center vertically and horizontally
    CENTER = Constant()


class Color(ConstantContainer):
    
    DEFAULT = (-1.0, -1.0, -1.0, -1.0)

    WHITE = (1.0, 1.0, 1.0, 1.0)
    
    BLACK = (0.0, 0.0, 0.0, 1.0)
    
    RED = (1.0, 0.0, 0.0, 1.0)

    DARK_RED = (0.5, 0.0, 0.0, 1.0)

    GREEN = (0.0, 1.0, 0.0, 1.0)
    
    DARK_GREEN = (0.0, 0.5, 0.0, 1.0)

    BLUE = (0.0, 0.0, 1.0, 1.0)
    
    DARK_BLUE = (0.0, 0.0, 0.5, 1.0)

    CYAN = (0.0, 1.0, 1.0, 1.0)
    
    DARK_CYAN = (0.0, 0.5, 0.5, 1.0)

    MAGENTA = (1.0, 0.0, 1.0, 1.0)

    DARK_MAGENTA = (0.5, 0.0, 0.5, 1.0)

    YELLOW = (1.0, 1.0, 0.0, 1.0)
    
    DARK_YELLOW = (0.5, 0.5, 0.0, 1.0)

    GRAY = (0.627, 0.627, 0.643, 1.0)
    
    DARK_GRAY = (0.5, 0.5, 0.5, 1.0)

    LIGHT_GRAY = (0.753, 0.753, 0.753, 1.0)

    TRANSPARENT = (0.0, 0.0, 0.0, 0.0)

    ERROR = (1.0, 0.75, 0.75, 1.0)
        

class Layout(ConstantContainer):

    DEFAULT = Constant()

    VERTICAL = Constant()

    HORIZONTAL = Constant()
    
    FORM = Constant()

    ABSOLUTE = Constant()


class Orientation(ConstantContainer):

    DEFAULT = Constant()

    HORIZONTAL = Constant()
    
    VERTICAL = Constant()


class SizePolicy(ConstantContainer):
    
    # These constant values are intended to be used in 
    # conjunction with the size_hint trait to determine
    # the sizing of a widget. There will be a size policy
    # flag for each of the horizontal and vertical directions.
    
    # Use the default sizing rules of the widget.
    DEFAULT = Constant()
    
    # size_hint is the fixed size of the widget.
    FIXED = Constant()

    # size_hint sets the minimum size of the widget.
    MINIMUM = Constant()

    # size_hint sets the maximum size of the widget.
    MAXIMUM = Constant()
    
    # size_hint is best but can be smaller. No benefit to being larger.
    PREFERRED = Constant()

    # size_hint is a suggestions but the widget can shrink and expand.
    EXPANDING = Constant()

    # size_hint is a minimum, but the widget should still be greedy.
    MINIMUM_EXPANDING = Constant()
    
    # size_hint is ignored and the widget gets as much space as possible.
    IGNORED = Constant()


class TabPosition(ConstantContainer):

    # The position of the tab bar in a TabGroup

    DEFAULT = Constant()

    TOP = Constant()

    BOTTOM = Constant()

    LEFT = Constant()

    RIGHT = Constant()


class TickPosition(ConstantContainer):
    
    # The tick position constants for a slider.
    
    DEFAULT = Constant()
    
    NO_TICKS = Constant()

    BOTH_SIDES = Constant()

    ABOVE = Constant()

    BELOW = Constant()

    LEFT = Constant()

    RIGHT = Constant()

class WindowRegion(ConstantContainer):
    """A button's location in a dialog window, for example."""
    
    DEFAULT = Constant()

    TOP_LEFT = Constant()

    TOP_CENTER = Constant()

    TOP_RIGHT = Constant()

    MIDDLE_LEFT = Constant()

    MIDDLE_CENTER = Constant()

    MIDDLE_RIGHT = Constant()

    BOTTOM_LEFT = Constant()

    BOTTOM_CENTER = Constant()

    BOTTOM_RIGHT = Constant()

class DialogType(ConstantContainer):
    """Predefined combinations of buttons to use in a dialog."""

    CLOSE = Constant()

    OK_CANCEL = Constant()

    ACCEPT_REJECT = Constant()

    YES_NO = Constant()

