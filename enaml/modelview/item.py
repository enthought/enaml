#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from traits.api import Any, Int, Enum, Str, Unicode, Property, Either, Instance

from enaml.core.declarative import Declarative
from enaml.core.trait_types import CoercingInstance
from enaml.layout.geometry import Size

from .enums import ItemFlag, CheckState, AlignmentFlag
from .utils import SlotData, SlotDataProperty


class ItemListener(object):
    """ An abstract base class for declaring item listeners.

    Classes can register themselves with this class if they wish to
    listen to slot data changes on child Item instances.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def on_item_changed(self, item, name):
        """ Implement this method to receive change notification.

        Parameters
        ----------
        item : Item
            The item instance which changed.

        name : str
            The name of the attribute on the item which changed.

        """
        raise NotImplementedError


class ItemData(SlotData):
    """ A slot data object for storing item attribute.

    """
    __slots__ = (
        'data', 'tool_tip', 'status_tip', 'background', 'foreground',
        'font', 'icon_source', 'flags', 'text_alignment', 'check_state',
        'size_hint', '_id'
    )

    def notify(self, item, name):
        """ Handle the slot's change notification.

        This handler will forward the change to notifier installed on
        the item.

        """
        parent = item.parent
        if isinstance(parent, ItemListener):
            parent.on_item_changed(item, name)


class Item(Declarative):
    """ A declarative class for creating items for item-based views.

    """
    # All of these attributes are declared as properties into a slotted
    # object to save memory. This is a bit of a hack, but hundreds of
    # thousands of these items may be created in large models, and
    # every little bit helps in those cases.

    #: The data held by the item. Subclasses may redefine this trait.
    data = SlotDataProperty('data')

    #: The data to use when editing the item. By default this is the
    #: same as `data`. Subclasses may redefine this trait.
    edit_data = Property(
        trait=Any,
        fget=lambda self: self.data,
        fset=lambda self, value: setattr(self, 'data', value)
    )

    #: The tool tip to use for the item.
    tool_tip = SlotDataProperty('tool_tip', Unicode)

    #: The status tip to use for the item.
    status_tip = SlotDataProperty('status_tip', Unicode)

    #: The background color of the item. Supports CSS3 color strings.
    background = SlotDataProperty('background', Str)

    #: The foreground color of the item. Supports CSS3 color strings.
    foreground = SlotDataProperty('foreground', Str)

    #: The font of the item. Supports CSS3 shorthand font strings.
    font = SlotDataProperty('font', Str)

    #: The source url for the icon to use for the item.
    icon_source = SlotDataProperty('icon_source', Str)

    #: The flags for the item. This should be an or'd combination of
    #: the ItemFlag enum values. By default, an item is enabled and
    #: selectable.
    flags = SlotDataProperty(
        'flags', Int,
        default=ItemFlag.ITEM_IS_ENABLED | ItemFlag.ITEM_IS_SELECTABLE
    )

    #: The alignment of text in the item. This should be an or'd
    #: combination of the AlignmentFlag enum values. By default, the
    #: text is centered vertically and horizontally.
    text_alignment = SlotDataProperty(
        'text_alignment', Int, default=AlignmentFlag.ALIGN_CENTER
    )

    #: The check state of the item. This should be None, or one of the
    #: CheckState enum values. The default is None.
    check_state = SlotDataProperty(
        'check_state', Enum(None, CheckState.UNCHECKED, CheckState.CHECKED)
    )

    #: The size hint for the item. The default value indicates that the
    #: size hint should be automatically determined by the toolkit.
    size_hint = SlotDataProperty(
        'size_hint', Either(None, CoercingInstance(Size))
    )

    #: A private attribute which can be used by item models to store
    #: a custom identifier for the item. This should not be modified
    #: by user code.
    _index = SlotDataProperty('_id', notify=False)

    #: The private storage for the ItemData instance for this item.
    #: This should not be manipulated by user code.
    _slot_data = Instance(ItemData, ())

