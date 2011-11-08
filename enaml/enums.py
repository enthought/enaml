#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum

from .util import enum

#: A dialog's result (depending on how it was closed)
#:
#: ============ ===============================================
#: value        description
#: ============ ===============================================
#: ``accepted`` (default) The user accepted the dialog.
#: ``rejected`` The user declined the default result.
#: ============ ===============================================
DialogResult = Enum(('accepted', 'rejected'))

#: Generic orientation values.
#:
#: ============== ======================
#: value          description
#: ============== ======================
#: ``horizontal`` Horizontal orientation
#: ``vertical``   Vertical orientation
#: ============== ======================
Orientation = Enum(('horizontal', 'vertical'))

#: The position of the tabs in a notebook.
#:
#: ========== =====================================================
#: value      description
#: ========== =====================================================
#: ``left``   (default) Place tabs to the left of the main content.
#: ``right``  Place tabs to the right of the main content.
#: ``top``    Place tabs above the main content.
#: ``bottom`` Place tabs below the main content.
#: ========== =====================================================
TabPosition = Enum(('left', 'right', 'top', 'bottom'))

#: A container's layout style, based on the order of insertion.
#:
#: ================= ===============================================
#: value             description
#: ================= ===============================================
#: ``left_to_right`` (default) Position children from left to right.
#: ``right_to_left`` Position children from right to left.
#: ``top_to_bottom`` Position children from top to bottom.
#: ``bottom_to_top`` Position children from bottom to top.
#: ================= ===============================================
Direction = Enum(('left_to_right', 'right_to_left',
                    'top_to_bottom', 'bottom_to_top'))

#: A window's modality specifies whether it captures focus.
#:
#: ===================== =================================================
#: value                 description
#: ===================== =================================================
#: ``non_modal``         (default) The window is not modal.
#: ``window_modal``      The window blocks input to its parent, and all
#:                       ancestor windows.
#: ``application_modal`` The window blocks input to all other windows in
#:                       the application.
#: ===================== =================================================
Modality = Enum(('non_modal', 'window_modal', 'application_modal'))

#: The position of ticks for a control.
#:
#: ============= =========================================================
#: value         description
#: ============= =========================================================
#: ``not_ticks`` (default) Do not display ticks.
#: ``left``      Display ticks to the left of the element.
#: ``right``     Display ticks to the right of the element.
#: ``top``       Display ticks above the element.
#: ``bottom``    Display ticks below the element.
#: ``both``      Display ticks both above the element and below it, or to
#:               both the left and the right. This might vary with
#:               :attr:`Orientation`.
#: ============= =========================================================
TickPosition = Enum(('no_ticks', 'left', 'right',
                     'top', 'bottom', 'both'))

#: The ordering of a sort.
#:
#: ============== =====================================
#: value          description
#: ============== =====================================
#: ``ascending``  Elements will be in ascending order.
#: ``descending`` Elements will be in descending order.
#: ============== =====================================
Sorted = Enum(('ascending', 'descending'))

#: The result of a validation function.
#:
#: ================ ======================================================
#: value            description
#: ================ ======================================================
#: ``invalid``      The input was clearly invalid.
#: ``indermediate`` The input is invalid, but further input could make it
#:                  valid.
#: ``acceptable``   The input is valid.
#: ================ ======================================================
Validity = Enum(('invalid', 'indermediate', 'acceptable'))

#: The strength of widget expand and clip preferences for hug and resist_clip.
#:
#: ================ ======================================================
#: value            description
#: ================ ======================================================
#: ``ignore``       No constraint shuld be created.
#: ``weak``         The constraint should be created, but is weak.
#: ``strong``       The constraint should be created, but is strong.
#: ``required``     The constraint should be created, and is required.
#: ================ ======================================================
PolicyEnum = Enum('ignore', 'weak', 'strong', 'required')


class Buttons(enum.Enum):
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


class DataRole(enum.Enum):
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


class ItemFlags(enum.Enum):
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


class Match(enum.Enum):
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
