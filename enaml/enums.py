from .util.enum import Enum


class Align(Enum):
   
    DEFAULT = 0x0

    LEFT = 0x1
    
    RIGHT = 0x2
    
    TOP = 0x4
    
    BOTTOM = 0x8
    
    CENTER = 0x10

    JUSTIFY = 0x20


class Buttons(Enum):

    NO_BUTTONS = 0x0

    OK = 0x1
    
    OPEN = 0x2
    
    SAVE = 0x4
    
    CANCEL = 0x8
    
    CLOSE = 0x10
    
    DISCARD = 0x20
    
    APPLY = 0x40
    
    RESET = 0x80
    
    RESTORE_DEFAULTS = 0x100
    
    HELP = 0x200
    
    SAVE_ALL = 0x400
    
    YES = 0x800
    
    YES_TO_ALL = 0x1000
    
    NO = 0x2000
    
    NO_TO_ALL = 0x4000
    
    ABORT = 0x8000
    
    RETRY = 0x10000
    
    IGNORE = 0x20000
    
    OK_CANCEL = OK | CANCEL
    
    YES_NO = YES | NO


class DialogResult(Enum):

    REJECTED = 0
    
    ACCEPTED = 1


class Direction(Enum):
    
    LEFT_TO_RIGHT = 0

    RIGHT_TO_LEFT = 1

    TOP_TO_BOTTOM = 2

    BOTTOM_TO_TOP = 3


class Modality(Enum):

    NON_MODAL = 0

    WINDOW_MODAL = 1

    APPLICATION_MODAL = 2


class Orientation(Enum):

    HORIZONTAL = 0
    
    VERTICAL = 1


class TabPosition(Enum):

    LEFT = 0

    RIGHT = 1

    TOP = 2

    BOTTOM = 3


class TickPosition(Enum):

    LEFT = 0

    RIGHT = 1

    TOP = 2

    BOTTOM = 3

    BOTH = 4

    NO_TICKS = 5

    DEFAULT = 6


class DataRole(Enum):

    DISPLAY = 0

    DECORATION = 1

    EDIT = 2

    TOOL_TIP = 3

    STATUS_TIP = 4

    WHATS_THIS = 5

    FONT = 6

    TEXT_ALIGNMENT = 7

    BACKGROUND = 8

    FOREGROUND = 9

    CHECK_STATE = 10

    SIZE_HINT = 11

    USER = 12

    # XXX - HACK!
    ALL = tuple(range(12))


class ItemFlags(Enum):

    NO_FLAGS = 0x0

    IS_SELECTABLE = 0x1

    IS_EDITABLE = 0x2

    IS_DRAG_ENABLED = 0x4

    IS_DROP_ENABLED = 0x8

    IS_USER_CHECKABLE = 0x10

    IS_ENABLED = 0x20

    IS_TRISTATE = 0x40


class Match(Enum):

    EXACTLY = 0x0

    CONTAINS = 0x1

    STARTS_WITH = 0x2

    ENDS_WITH = 0x4

    REG_EXP = 0x8

    WILD_CARD = 0x10

    FIXED_STRING = 0x20

    CASE_SENSITIVE = 0x40

    WRAP = 0x80

    RECURSIVE = 0x100


class Sorted(Enum):

    ASCENDING = 0

    DESCENDING = 1

