#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Any, Int, Enum, Str, Unicode, Instance, Property

from enaml.core.declarative import Declarative
from enaml.core.trait_types import CoercingInstance
from enaml.layout.geometry import Size

from .edit_widgets import EditWidget
from .enums import ItemFlag, CheckState, AlignmentFlag


class Item(Declarative):
    """ A declarative class for creating items for item-based views.

    """
    #: The data held by the item. Subclasses may redefine this trait.
    data = Any

    #: The value to use when editing the item. By default this is the
    #: same as `value`. Subclasses may redefine this trait.
    edit_data = Property(
        fget=lambda self: self.data,
        fset=lambda self, value: setattr(self, 'data', value)
    )

    #: The tool tip to use for the item.
    tool_tip = Unicode

    #: The status tip to use for the item.
    status_tip = Unicode

    #: The background color of the item. Supports CSS3 color strings.
    background = Str

    #: The foreground color of the item. Supports CSS3 color strings.
    foreground = Str

    #: The font of the item. Supports CSS3 shorthand font strings.
    font = Str

    #: The source url for the icon to use for the item.
    icon_source = Str

    #: The flags for the item. This should be an or'd combination of
    #: the ItemFlag enum values. By default, an item is enabled and
    #: selectable.
    flags = Int(ItemFlag.ITEM_IS_ENABLED | ItemFlag.ITEM_IS_SELECTABLE)

    #: The alignment of text in the item. This should be an or'd
    #: combination of the AlignmentFlag enum values. By default, the
    #: text is centered vertically and horizontally.
    text_alignment = Int(AlignmentFlag.ALIGN_CENTER)

    #: The check state of the item. This should be None, or one of the
    #: CheckState enum values. The default is None.
    check_state = Enum(None, CheckState.UNCHECKED, CheckState.CHECKED)

    #: The size hint for the item. The default value indicates that the
    #: size hint should be automatically determined by the toolkit.
    size_hint = CoercingInstance(Size, (-1, -1))

    #: The widget to use when editing the item in the ui. If none is
    #: provided, the toolkit will choose an appropriate default.
    edit_widget = Instance(EditWidget)

