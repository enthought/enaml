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
    flags = Int(
        ItemFlag.ITEM_IS_ENABLED |
        ItemFlag.ITEM_IS_SELECTABLE |
        ItemFlag.ITEM_IS_EDITABLE
    )


class BaseStringEdit(EditableItem):
    """ An `EditableItem` subclass which left aligns text.

    """
    #: The string data of the editor.
    data = Instance(basestring)

    #: By default, string data is left aligned.
    text_alignment = AlignmentFlag.ALIGN_LEFT | AlignmentFlag.ALIGN_V_CENTER


class StringEdit(BaseStringEdit):
    """ A `BaseStringEdit` subclass for editing plain strings.

    """
    #: The plain string data of the editor.
    data = Str


class UnicodeEdit(BaseStringEdit):
    """ An `BaseStringEdit` subclass for editing unicode strings.

    """
    #: The unicode string data of the editor.
    data = Unicode


class NumberEdit(EditableItem):
    """ An `EditableItem` subclass which right aligns numbers.

    """
    #: The number data of the editor.
    data = Instance('numbers.Number')

    #: By default, numeric data is right aligned.
    text_alignment = AlignmentFlag.ALIGN_RIGHT | AlignmentFlag.ALIGN_V_CENTER


class IntEdit(NumberEdit):
    """ An `NumberEdit` subclass for editing integers.

    """
    #: The integer data of the editor.
    data = Int


class LongEdit(NumberEdit):
    """ An `NumberEdit` subclass for editing longs.

    """
    #: The long integer data of the editor.
    data = Long


class FloatEdit(NumberEdit):
    """ An `NumberEdit` subclass for editing floats.

    """
    #: The float data of the editor.
    data = Float


class DateEdit(EditableItem):
    """ An `EditableItem` subclass for editing dates.

    """
    #: The date data of the editor.
    data = Instance(date, factory=date.today)


class TimeEdit(EditableItem):
    """ An `EditableItem` subclass for editing times.

    """
    #: The time data of the editor.
    data = Instance(time, factory=lambda: datetime.now().time())


class DateTimeEdit(EditableItem):
    """ An `EditableItem` subclass for editing datetimes.

    """
    #: The datetime data of the editor.
    data = Instance(datetime, factory=datetime.now)

