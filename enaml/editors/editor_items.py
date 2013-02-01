#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from datetime import date, time, datetime

from traits.api import Any, Bool, Str, Unicode, Int, Long, Float, Instance

from .item import Item


class EditorItem(Item):
    """ A concrete `Item` class which supports editing a value.

    """
    #: By default, an `EditorItem` is editable.
    editable = True

    #: The value of the editor item. Subclasses should redifine this
    #: trait to enforce appropriate type checking.
    value = Any

    def data(self):
        """ Get the data for the item.

        Returns
        -------
        result : object
            The data to be displayed by the item.

        """
        return self.value

    def set_data(self, value):
        """ Set the data for the item.

        The default implementation of this method assigns the value to
        the `value` attribute. Subclasses may reimplement this method
        as needed.

        Returns
        -------
        result : bool
            The method returns True after successful setting the
            attribute.

        """
        self.value = value
        return True


class StringEditor(EditorItem):
    """ An `EditorItem` subclass for editing plain strings.

    """
    #: The plain string value of the editor.
    value = Str


class UnicodeEditor(EditorItem):
    """ An `EditorItem` subclass for editing unicode strings.

    """
    #: The unicode string value of the editor.
    value = Unicode


class IntEditor(EditorItem):
    """ An `EditorItem` subclass for editing integers.

    """
    #: The integer value of the editor.
    value = Int


class LongEditor(EditorItem):
    """ An `EditorItem` subclass for editing longs.

    """
    #: The long integer value of the editor.
    value = Long


class FloatEditor(EditorItem):
    """ An `EditorItem` subclass for editing floats.

    """
    #: The float value of the editor.
    value = Float


class BoolEditor(EditorItem):
    """ An `EditorItem` subclass for editing bools.

    """
    #: The boolean value of the editor.
    value = Bool


class DateEditor(EditorItem):
    """ An `EditorItem` subclass for editing dates.

    """
    #: The date value of the editor.
    value = Instance(date, factory=date.today)


class TimeEditor(EditorItem):
    """ An `EditorItem` subclass for editing times.

    """
    #: The date value of the editor.
    value = Instance(time, factory=lambda: datetime.now().time())


class DateTimeEditor(EditorItem):
    """ An `EditorItem` subclass for editing datetimes.

    """
    #: The date value of the editor.
    value = Instance(datetime, factory=datetime.now)

