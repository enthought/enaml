#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Enum, Str, Unicode

from enaml.core.messenger import Messenger
from enaml.core.trait_types import CoercingInstance
from enaml.layout.geometry import Size


class ListItem(Messenger):
    """ A `ListItem` is used as an item in a `ListWidget`.

    """
    #: The text to display in the item.
    text = Unicode

    #: The tool tip to use for the item.
    tool_tip = Unicode

    #: The status tip to use for the item.
    status_tip = Unicode

    #: The background color of the item. Supports CSS3 color strings.
    background = Str

    #: The foreground color of the item. Supports CSS3 color strings.
    foreground = Str

    #: The font used for the widget. Supports CSS font formats.
    font = Str

    #: The source url for the icon to use for the item.
    icon_source = Str

    #: Whether or not the item can be checked.
    checkable = Bool(False)

    #: Whether or not the item is checked. This value only has meaning
    #: if 'checkable' is set to True.
    checked = Bool(False)

    #: Whether or not the item can be selected.
    selectable = Bool(True)

    #: Whether or not the item is selected. This value only has meaning
    #: if 'selectable' is set to True.
    selected = Bool(False)

    #: Whether or not the item is enabled.
    enabled = Bool(True)

    #: Whether or not the item is visible.
    visible = Bool(True)

    #: The horizontal alignment of the text in the item area.
    text_align = Enum('left', 'right', 'center', 'justify')

    #: The vertical alignment of the text in the item area.
    vertical_text_align = Enum('center', 'top', 'bottom')

    #: The preferred size of the item.
    preferred_size = CoercingInstance(Size, (-1, -1))

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dictionary for the list item.

        """
        snap = super(ListItem, self).snapshot()
        snap['text'] = self.text
        snap['tool_tip'] = self.tool_tip
        snap['status_tip'] = self.status_tip
        snap['background'] = self.background
        snap['foreground'] = self.foreground
        snap['font'] = self.font
        snap['icon_source'] = self.icon_source
        snap['checkable'] = self.checkable
        snap['checked'] = self.checked
        snap['selectable'] = self.selectable
        snap['selected'] = self.selected
        snap['enabled'] = self.enabled
        snap['visible'] = self.visible
        snap['text_align'] = self.text_align
        snap['vertical_text_align'] = self.vertical_text_align
        snap['preferred_size'] = self.preferred_size
        return snap

    def bind(self):
        """ Bind the change handlers for the list item.

        """
        super(ListItem, self).bind()
        attrs = (
            'text', 'tool_tip', 'status_tip', 'background', 'foreground',
            'font', 'icon_source', 'checkable', 'checked', 'selectable',
            'selected', 'enabled', 'visible', 'preferred_size', 'text_align',
            'vertical_text_align',
        )
        self.publish_attributes(*attrs)

