#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Enum, Str, Unicode

from enaml.core.messenger import Messenger
from enaml.core.trait_types import CoercingInstance, EnamlEvent
from enaml.layout.geometry import Size


class ListItem(Messenger):
    """ A non-widget used as an item in a `ListControl`

    A `ListItem` represents an item in a `ListControl`. It contains all
    of the information needed for data and styling.

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

    #: The font used for the widget. Supports CSS3 shorthand font strings.
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

    #: Whether or not the item is selected. This value only has meaning
    #: if 'selectable' is set to True.
    selected = Bool(False)

    #: Whether or not the item is editable.
    editable = Bool(False)

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

    #: An event fired when the user clicks on the item. The payload
    #: will be the current checked state of the item.
    clicked = EnamlEvent

    #: An event fired when the user double clicks on the item. The
    #: payload will be the current checked state of the item.
    double_clicked = EnamlEvent

    #: An event fired when the user toggles a checkable item. The
    #: payload will be the current checked state of the item.
    toggled = EnamlEvent

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
        snap['editable'] = self.editable
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
            'selected', 'editable', 'enabled', 'visible', 'preferred_size',
            'text_align', 'vertical_text_align',
        )
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_clicked(self, content):
        """ Handle the 'clicked' action from the client widget.

        """
        self.clicked(self.checked)

    def on_action_double_clicked(self, content):
        """ Handle the 'double_clicked' action from the client widget.

        """
        self.double_clicked(self.checked)

    def on_action_changed(self, content):
        """ Handle the 'changed' action from the client widget.

        """
        old_checked = self.checked
        new_checked = content['checked']
        was_toggled = old_checked != new_checked
        if was_toggled:
            self.set_guarded(checked=new_checked)
        self.set_guarded(text=content['text'])
        if was_toggled:
            self.toggled(new_checked)

