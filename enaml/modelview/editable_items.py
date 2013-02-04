#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from datetime import date, time, datetime

from traits.api import Str, Unicode, Int, Long, Float, Instance

from .enums import ItemFlag, AlignmentFlag
from .item import Item


class EditableItem(Item):
    """ A `Item` class which supports editing a value by default.

    """
    #: By default, the item is enabled, selectable, and editable.
    flags = (
        ItemFlag.ITEM_IS_ENABLED |
        ItemFlag.ITEM_IS_SELECTABLE |
        ItemFlag.ITEM_IS_EDITABLE
    )


class LeftAlignedEdit(EditableItem):
    """ An `EditableItem` subclass which aligns the data to the left.

    """
    #: By default, the data is left aligned.
    text_alignment = AlignmentFlag.ALIGN_LEFT | AlignmentFlag.ALIGN_V_CENTER


class RightAlignedEdit(EditableItem):
    """ An `EditableItem` subclass which aligns the data to the right.

    """
    #: By default, the data is right aligned.
    text_alignment = AlignmentFlag.ALIGN_RIGHT | AlignmentFlag.ALIGN_V_CENTER


class StringEdit(LeftAlignedEdit):
    """ A `LeftAlignedEdit` subclass for editing plain strings.

    """
    #: The plain string data of the editor.
    data = Str


class UnicodeEdit(LeftAlignedEdit):
    """ An `LeftAlignedEdit` subclass for editing unicode strings.

    """
    #: The unicode string data of the editor.
    data = Unicode


class IntEdit(RightAlignedEdit):
    """ An `RightAlignedEdit` subclass for editing integers.

    """
    #: The integer data of the editor.
    data = Int


class LongEdit(RightAlignedEdit):
    """ An `RightAlignedEdit` subclass for editing longs.

    """
    #: The long integer data of the editor.
    data = Long


class FloatEdit(RightAlignedEdit):
    """ An `RightAlignedEdit` subclass for editing floats.

    """
    #: The float data of the editor.
    data = Float


class DateEdit(RightAlignedEdit):
    """ A `RightAlignedEdit` subclass for editing dates.

    """
    #: The date data of the editor.
    data = Instance(date, factory=date.today)


class TimeEdit(RightAlignedEdit):
    """ A `RightAlignedEdit` subclass for editing times.

    """
    #: The time data of the editor.
    data = Instance(time, factory=lambda: datetime.now().time())


class DateTimeEdit(RightAlignedEdit):
    """ A `RightAlignedEdit` subclass for editing datetimes.

    """
    #: The datetime data of the editor.
    data = Instance(datetime, factory=datetime.now)

