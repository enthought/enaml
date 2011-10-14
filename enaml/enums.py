#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .util.enum import Enum


class Align(Enum):
    """ Elements' alignment in a container. 

    """
    #: The default alignment.
    DEFAULT = 0x0

    #: Elements align with the left edge.
    LEFT = 0x1
    
    #: Elements align with the right edge.
    RIGHT = 0x2
    
    #: Elements align with the top edge.
    TOP = 0x4
    
    #: Elements align with the bottom edge.
    BOTTOM = 0x8
    
    #: The elements are centered.
    CENTER = 0x10

    #: The elements are justified.
    JUSTIFY = 0x20


class Buttons(Enum):
    """ Predefined text labels for buttons. 

    """
    #: Do not display buttons.
    NO_BUTTONS = 0x0

    #: Agree.
    OK = 0x1
    
    #: Open.
    OPEN = 0x2
    
    #: Save changes.
    SAVE = 0x4
    
    #: Reject changes.
    CANCEL = 0x8
    
    #: Close without accepintg.
    CLOSE = 0x10
    
    #: Discard changes.
    DISCARD = 0x20
    
    #: Apply changes.
    APPLY = 0x40
    
    #: Reset changes.
    RESET = 0x80
    
    #: Restore defaults.
    RESTORE_DEFAULTS = 0x100
    
    #: Get help.
    HELP = 0x200
    
    #: Save all changes.
    SAVE_ALL = 0x400
    
    #: Accept once.
    YES = 0x800
    
    #: Accept this choice, and subsequent choices.
    YES_TO_ALL = 0x1000
    
    #: Reject once.
    NO = 0x2000
    
    #: Reject this choice, and subsequent choices.
    NO_TO_ALL = 0x4000
    
    #: Abort updates.
    ABORT = 0x8000
    
    #: Retry action.
    RETRY = 0x10000
    
    #: Ignore.
    IGNORE = 0x20000
    
    #: Display both an `OK` button and a `CANCEL` button.
    OK_CANCEL = OK | CANCEL
    
    #: Display both a `YES` button and a `NO` button.
    YES_NO = YES | NO


class DialogResult(Enum):
    """ A dialog's result, depending on how it was closed. 

    """
    #: The user declined -- the default result.
    REJECTED = 0
    
    #: The user accepted the dialog.
    ACCEPTED = 1


class Direction(Enum):
    """ A container's layout style, based on the order of insertion. 

    """
    #: Position children from left to right.
    LEFT_TO_RIGHT = 0

    #: Position children from right to left.
    RIGHT_TO_LEFT = 1

    #: Position children from top to bottom.
    TOP_TO_BOTTOM = 2

    #: Position children from bottom to top.
    BOTTOM_TO_TOP = 3


class Modality(Enum):
    """ A window's modality specifies whether it captures focus. 

    """
    #: The window is not modal.
    NON_MODAL = 0

    #: The window blocks input to its parent, and all ancestor windows.
    WINDOW_MODAL = 1

    #: The window blocks input to all other windows in the application.
    APPLICATION_MODAL = 2


class Orientation(Enum):
    """ An element's layout. 

    """
    #: Positioned from left to right, or right to left.
    HORIZONTAL = 0
    
    #: Positioned from top to bottom, or bottom to top.
    VERTICAL = 1


class TabPosition(Enum):
    """ The position of tabs in a notebook. 

    """
    #: Place tabs to the left of the main content.
    LEFT = 0

    #: Place tabs to the right of the main content.
    RIGHT = 1

    #: Place tabs above the main content.
    TOP = 2

    #: Place tabs below the main content.
    BOTTOM = 3


class TickPosition(Enum):
    """ The position of ticks for a control. 

    """
    #: Display ticks to the left of the element.
    LEFT = 0

    #: Display ticks to the right of the element.
    RIGHT = 1

    #: Display ticks above the element.
    TOP = 2

    #: Display ticks below the element.
    BOTTOM = 3

    #: Display ticks both above the element and below it, or to
    #: both the left and the right.
    #:
    #: This might vary with `Orientation`.
    BOTH = 4

    #: Do not display ticks.
    NO_TICKS = 5

    #: Display ticks in the default position for the toolkit.
    DEFAULT = 6


class DataRole(Enum):
    """ The type or purpose of data in a model. 

    """
    #: Display data prominently, as text.
    DISPLAY = 0

    #: Render the data as an icon.
    DECORATION = 1

    #: Render the data in an editor-friendly form.
    EDIT = 2

    #: Display the data as tooltip text.
    TOOL_TIP = 3

    #: Display the data in the status bar.
    STATUS_TIP = 4

    #: Display the data for "What's This?" mode.
    WHATS_THIS = 5

    #: The data specifies a font.
    FONT = 6

    #: The data specifies text alignment.
    TEXT_ALIGNMENT = 7

    #: The data represents a background display style.
    BACKGROUND = 8

    #: The data represents a foreground display style.
    FOREGROUND = 9

    #: Determine whether an item is in the checked state.
    CHECK_STATE = 10

    #: The data is a size hint for display in views.
    SIZE_HINT = 11

    #: The data corresponds to a user.
    USER = 12

    # XXX - HACK!
    #: A tuple containing all display roles.
    ALL = tuple(range(12))


class ItemFlags(Enum):
    """ Specify the actions that can be performed on model items. 

    """
    #: The item is not configured for user interaction via a view.
    NO_FLAGS = 0x0

    #: The item can be selected in a view.
    IS_SELECTABLE = 0x1

    #: The item can be edited in a view.
    IS_EDITABLE = 0x2

    #: The item can be dragged.
    IS_DRAG_ENABLED = 0x4

    #: Another item can be dropped onto this one.
    IS_DROP_ENABLED = 0x8

    #: The item's "checked" state can be changed from a view.
    IS_USER_CHECKABLE = 0x10

    #: This item permits user interaction in a view.
    IS_ENABLED = 0x20

    #: The item is checkable, and it has three distinct states.
    IS_TRISTATE = 0x40


class Match(Enum):
    """ The type of a text search. 

    """
    #: An exact match.
    EXACTLY = 0x0

    #: The data contains the sought item.
    CONTAINS = 0x1

    #: The data starts with the search term.
    STARTS_WITH = 0x2

    #: The data ends with the search term.
    ENDS_WITH = 0x4

    #: A regular expression match.
    REG_EXP = 0x8

    #: Match all items.
    WILD_CARD = 0x10

    #: Search for a string literal.
    FIXED_STRING = 0x20

    #: Search in a case-sensitive manner.
    CASE_SENSITIVE = 0x40

    #: Wrap from the bottom of the text to the top. Continue searching.
    WRAP = 0x80

    #: Search recursively.
    RECURSIVE = 0x100


class Sorted(Enum):
    """ The ordering of a sort. 

    """
    #: Elements will be in ascending order.
    ASCENDING = 0

    #: Elements will be in descending order.
    DESCENDING = 1


class Validity(Enum):
    """ The result of a validation function. 

    """
    #: The input was clearly invalid.
    INVALID = 0x0
    
    #: The input is invalid, but further input could make it valid.
    INTERMEDIATE = 0x1
    
    #: The input is valid.
    ACCEPTABLE = 0x2


class PolicyFlag(Enum):
    """ The policy flags used to create the SizePolicy values. This
    Enum is not meant to be used directly. Use the SizePolicy Enum
    instead.

    """
    #: The size_hint is the only acceptable size
    FIXED = 0x0

    #: The widget can grow beyond the size hint if necessary.
    GROW = 0x1

    #: The widget should get as much space as possible
    EXPAND = 0x2

    #: The widget can shrink below its size hint if necessary.
    SHRINK = 0x4

    #: The size hint is ignored. Widget will get as much space as possible.
    IGNORE = 0x8


class SizePolicy(Enum):
    """ The size policy for a given widget. The size policy indicates 
    how the widget should be resized when placed in a layout.

    """
    #: Use the default size policy of the widget.
    DEFAULT = -1

    #: The size hint is a minimum. The widget can be expanded if necessary.
    MINIMUM = PolicyFlag.GROW

    #: The size hint is a maximum. The widget can be shrunk if necessary.
    MAXIMUM = PolicyFlag.SHRINK

    #: The size hint is best, but the widget can grow or shrink if necessary.
    PREFERRED = PolicyFlag.GROW | PolicyFlag.SHRINK

    #: The size hint is sensible, but the widget can be shrunk and still 
    #: be useful. The widget should however get as much space as possible.
    EXPANDING = PolicyFlag.GROW | PolicyFlag.SHRINK | PolicyFlag.EXPAND

    #: The size hint is a minimum, but the widget can make used of extra
    #: space and so should get as much space as possible
    MINIMUM_EXPANDNING = PolicyFlag.GROW | PolicyFlag.EXPAND
    
    #: The size hint is ignored, and the widget will get as much space
    #: as possible.
    IGNORED = PolicyFlag.SHRINK | PolicyFlag.GROW | PolicyFlag.IGNORE

