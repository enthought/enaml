from .util.enum import Constant, Enum


class Align(Enum):
   
    DEFAULT = Constant()

    LEFT = Constant()
    
    RIGHT = Constant()
    
    TOP = Constant()
    
    BOTTOM = Constant()
    
    CENTER = Constant()

    JUSTIFY = Constant()


class Border(Enum):

    DEFAULT = Constant()

    NO_BORDER = Constant()

    DOTTED = Constant()

    DASHED = Constant()

    SOLID = Constant()

    RAISED = Constant()

    SUNKEN = Constant()


class Buttons(Enum):

    DEFAULT = Constant()

    OK = Constant()
    
    OPEN = Constant()
    
    SAVE = Constant()
    
    CANCEL = Constant()
    
    CLOSE = Constant()
    
    DISCARD = Constant()
    
    APPLY = Constant()
    
    RESET = Constant()
    
    RESTORE_DEFAULTS = Constant()
    
    HELP = Constant()
    
    SAVE_ALL = Constant()
    
    YES = Constant()
    
    YES_TO_ALL = Constant()
    
    NO = Constant()
    
    NO_TO_ALL = Constant()
    
    ABORT = Constant()
    
    RETRY = Constant()
    
    IGNORE = Constant()


class Color(Enum):
    
    DEFAULT = Constant((-1.0, -1.0, -1.0, -1.0))

    WHITE = Constant((1.0, 1.0, 1.0, 1.0))
    
    BLACK = Constant((0.0, 0.0, 0.0, 1.0))
    
    RED = Constant((1.0, 0.0, 0.0, 1.0))

    DARK_RED = Constant((0.5, 0.0, 0.0, 1.0))

    GREEN = Constant((0.0, 1.0, 0.0, 1.0))
    
    DARK_GREEN = Constant((0.0, 0.5, 0.0, 1.0))

    BLUE = Constant((0.0, 0.0, 1.0, 1.0))
    
    DARK_BLUE = Constant((0.0, 0.0, 0.5, 1.0))

    CYAN = Constant((0.0, 1.0, 1.0, 1.0))
    
    DARK_CYAN = Constant((0.0, 0.5, 0.5, 1.0))

    MAGENTA = Constant((1.0, 0.0, 1.0, 1.0))

    DARK_MAGENTA = Constant((0.5, 0.0, 0.5, 1.0))

    YELLOW = Constant((1.0, 1.0, 0.0, 1.0))
    
    DARK_YELLOW = Constant((0.5, 0.5, 0.0, 1.0))

    GRAY = Constant((0.627, 0.627, 0.643, 1.0))
    
    DARK_GRAY = Constant((0.5, 0.5, 0.5, 1.0))

    LIGHT_GRAY = Constant((0.753, 0.753, 0.753, 1.0))

    TRANSPARENT = Constant((0.0, 0.0, 0.0, 0.0))

    ERROR = Constant((1.0, 0.75, 0.75, 1.0))
        

class DialogResult(Enum):

    REJECTED = Constant()
    
    ACCEPTED = Constant()


class Direction(Enum):
    
    LEFT_TO_RIGHT = Constant()

    RIGHT_TO_LEFT = Constant()

    TOP_TO_BOTTOM = Constant()

    BOTTOM_TO_TOP = Constant()


class Modality(Enum):
    
    DEFAULT = Constant()

    NON_MODAL = Constant()

    WINDOW_MODAL = Constant()

    APPLICATION_MODAL = Constant()


class Orientation(Enum):

    DEFAULT = Constant()

    HORIZONTAL = Constant()
    
    VERTICAL = Constant()


class SizePolicy(Enum):

    DEFAULT = Constant()
    
    FIXED = Constant()

    MINIMUM = Constant()

    MAXIMUM = Constant()
    
    PREFERRED = Constant()

    EXPANDING = Constant()

    MINIMUM_EXPANDING = Constant()

    IGNORED = Constant()


class TabPosition(Enum):

    DEFAULT = Constant()

    LEFT = Constant()

    RIGHT = Constant()

    TOP = Constant()

    BOTTOM = Constant()


class TickPosition(Enum):
    
    DEFAULT = Constant()

    LEFT = Constant()

    RIGHT = Constant()

    TOP = Constant()

    BOTTOM = Constant()

    BOTH = Constant()

    NO_TICKS = Constant()


