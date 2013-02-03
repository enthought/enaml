#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
class ItemDataRole(object):
    """ The enum values for the item data roles.

    These enum values are equivalent to the Qt::ItemDataRole values.

    """
    DISPLAY_ROLE = 0

    DECORATION_ROLE = 1

    EDIT_ROLE = 2

    TOOL_TIP_ROLE = 3

    STATUS_TIP_ROLE = 4

    FONT_ROLE = 6

    TEXT_ALIGNMENT_ROLE = 7

    BACKGROUND_ROLE = 8

    FOREGROUND_ROLE = 9

    CHECK_STATE_ROLE = 10

    SIZE_HINT_ROLE = 13

    EDIT_WIDGET_ROLE = 33   # > Qt::UserRole


class ItemFlag(object):
    """ The enum values for item flags.

    These enum values are equivalent to the Qt::ItemFlag values.

    """
    NO_ITEM_FLAGS = 0x0

    ITEM_IS_SELECTABLE = 0x1

    ITEM_IS_EDITABLE = 0x2

    # TODO: ITEM_IS_DRAG_ENABLED = 0x4

    # TODO: ITEM_IS_DROP_ENABLED = 0x8

    ITEM_IS_USER_CHECKABLE = 0x10

    ITEM_IS_ENABLED = 0x20

    # TODO: ITEM_IS_TRISTATE = 0x40


class CheckState(object):
    """ The enum values for item check state.

    These enum values are equivalent to the Qt::CheckState values.

    """
    UNCHECKED = 0

    # TODO: PARTIALLY_CHECKED = 1

    CHECKED = 2


class AlignmentFlag(object):
    """ The enum values for alignment.

    These enum values are equivalent to the Qt::AlignmentFlag values.

    """
    ALIGN_LEFT = 0x1

    ALIGN_RIGHT = 0x2

    ALIGN_H_CENTER = 0x4

    ALIGN_JUSTIFY = 0x8

    ALIGN_TOP = 0x20

    ALIGN_BOTTOM = 0x40

    ALIGN_V_CENTER = 0x80

    ALIGN_CENTER = ALIGN_H_CENTER | ALIGN_V_CENTER

    ALIGN_HORIZONTAL_MASK = (
        ALIGN_LEFT | ALIGN_RIGHT | ALIGN_H_CENTER | ALIGN_JUSTIFY
    )

    ALIGN_VERTICAL_MASK = (ALIGN_TOP | ALIGN_BOTTOM | ALIGN_V_CENTER)

