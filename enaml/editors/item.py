#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Any, Bool, Enum, Str, Unicode, Instance

from enaml.core.declarative import Declarative
from enaml.core.trait_types import CoercingInstance
from enaml.layout.geometry import Size

from .editor_widgets import EditorWidget


class Item(Declarative):
    """ A base class for creating items for item-based views.

    """
    #: The tool tip to use for the item.
    tool_tip = Unicode

    #: The status tip to use for the item.
    status_tip = Unicode

    #: The background color of the item. Supports CSS3 color strings.
    #: If this is not provided, the item will inherit the background
    #: according to rules appropriate for the item.
    background = Str

    #: The foreground color of the item. Supports CSS3 color strings.
    #: If this is not provided, the item will inherit the foreground
    #: according to rules appropriate for the item.
    foreground = Str

    #: The font of the item. Supports CSS3 shorthand font strings. If
    #: this is not provided, the item will inherit the font according
    #: to rules appropriate for the item.
    font = Str

    #: The source url for the icon to use for the item.
    icon_source = Str

    #: Whether or not the item can be checked by the user. This has no
    #: bearing on whether or not a checkbox is visible for the item.
    #: For controlling the visibility of the checkbox, see `checked`.
    checkable = Bool(False)

    #: Whether or not the item is checked. A value of None indicates
    #: that no check box should be visible for the item.
    checked = Enum(None, False, True)

    #: Whether or not the item can be selected.
    selectable = Bool(True)

    #: Whether or not the item is editable.
    editable = Bool(False)

    #: The widget to use when editing the item in the ui. If none is
    #: provided, the toolkit will choose an appropriate default for
    #: the type of the data in the item. Providing an editor widget
    #: only makes sense if the item's `editable` flag is True.
    editor_widget = Instance(EditorWidget)

    #: Whether or not the item is enabled.
    enabled = Bool(True)

    #: Whether or not the item is visible. This may not be supported
    #: in all views; e.g. in grid views where having a non-visible
    #: cell is not possible.
    visible = Bool(True)

    #: The horizontal alignment of the text in the item area.
    text_align = Enum('left', 'right', 'center', 'justify')

    #: The vertical alignment of the text in the item area.
    vertical_text_align = Enum('center', 'top', 'bottom')

    #: The preferred size of the item.
    preferred_size = CoercingInstance(Size, (-1, -1))

    #: Private storage for toolkit data. This can be used by a toolkit
    #: backend to store anything it needs to associate with the item.
    #: This can be convenient for caching expensive to compute data,
    #: where the lifetime of the data should be bound to the lifetime
    #: of the item.
    _toolkit_data = Any

    def data(self):
        """ Get the data for this item.

        This method must be implemented by subclasses.

        Returns
        -------
        result : object
            The data to be displayed by this item.

        """
        raise NotImplementedError

    def set_data(self, value):
        """ Set the data for this item.

        This method will only be called if the `editable` flag is set
        to True, and the user attempts to edit the value from the ui.

        This method should be reimplemented as need to enable editing
        behavior on items.

        Returns
        -------
        result : bool
            Whether or not setting the data was sucessful. By default
            this method returns False.

        """
        return False

