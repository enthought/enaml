#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from collections import defaultdict

from .abstract_models import AbstractItemModel
from .enums import ItemDataRole, ItemFlag
from .model_editor import ModelEditor
from .header_group import HeaderGroup


#: Use blist if available; it allows O(log(n)) random inserts.
try:
    from blist import blist
    list_class = blist
except ImportError:
    list_class = list


class ItemModel(AbstractItemModel):
    """ A concrete implementation of AbstractItemModel.

    An `ItemModel` is designed to be used with the `ModelEditor` and
    `HeaderGroup` class. It uses these to create an `Item` instance for
    each cell in the model. It is reasonably efficient for models up to\
    ~100k items.

    """
    role_handlers = {
        ItemDataRole.DISPLAY_ROLE: '_item_display',
        ItemDataRole.DECORATION_ROLE: '_item_decoration',
        ItemDataRole.EDIT_ROLE: '_item_edit',
        ItemDataRole.TOOL_TIP_ROLE: '_item_tool_tip',
        ItemDataRole.STATUS_TIP_ROLE: '_item_status_tip',
        ItemDataRole.FONT_ROLE: '_item_font',
        ItemDataRole.TEXT_ALIGNMENT_ROLE: '_item_text_alignment',
        ItemDataRole.BACKGROUND_ROLE: '_item_background',
        ItemDataRole.FOREGROUND_ROLE: '_item_foreground',
        ItemDataRole.CHECK_STATE_ROLE: '_item_check_state',
        ItemDataRole.SIZE_HINT_ROLE: '_item_size_hint',
        ItemDataRole.EDIT_WIDGET_ROLE: '_item_edit_widget',
    }

    def __init__(self):
        """ Initialize an ItemModel.

        Parameters
        ----------
        header_location : str
            The location to place the headers relative to the data.
            The default is 'top'. Allowable locations are

        """
        self._row_count = 0
        self._column_count = 0
        self._header_location = 'left'
        self._header_groups = list_class()
        self._model_editors = list_class()
        self._items = list_class()
        self._transposed = False

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def add_header_group(self, group):
        """

        """
        assert isinstance(group, HeaderGroup)
        self._header_groups.append(group)

    def add_model_editor(self, editor):
        """

        """
        assert isinstance(editor, ModelEditor)
        self._model_editors.append(editor)

    def layout(self):
        """

        """
        header_groups = self._header_groups
        model_editors = self._model_editors

        # Compute the header items that will be used.
        header_items = []
        target_groups = set()
        for header_group in header_groups:
            target_groups.add(header_group.name)
            for header_item in header_group.items():
                header_items.append(header_item)

        # Compute the items available from each model. Each gets its
        # own list of items appended to the `model_items` list.
        model_items = []
        for model_editor in model_editors:
            # There can be multiple EditGroups with the same name.
            # Pass over them and merge the items into a dict. The
            # conflict resolution dictates that the last item with
            # the given name wins.
            edit_group_items = defaultdict(dict)
            for edit_group in model_editor.edit_groups():
                if edit_group.name in target_groups:
                    edit_items = edit_group_items[edit_group.name]
                    for edit_item in edit_group.items():
                        edit_items[edit_item.name] = edit_item

            # Pull out the items relevant for the headers. Fill in the
            # missing items with None
            these_items = []
            for header_item in header_items:
                group_name = header_item.parent.name
                if group_name in edit_group_items:
                    group_items = edit_group_items[group_name]
                    if header_item.name in group_items:
                        these_items.append(group_items[header_item.name])
                        continue
                these_items.append(None)
            model_items.append(these_items)

        # Assemble the final items list based on the header location.
        items = self._items = list_class()
        header_location = self._header_location
        if header_location == 'top':
            self._row_count = len(model_items) + 1
            self._column_count = len(header_items)
            items.extend(header_items)
            for row in model_items:
                items.extend(row)
        elif header_location == 'bottom':
            self._row_count = len(model_items) + 1
            self._column_count = len(header_items)
            for row in model_items:
                items.extend(row)
            items.extend(header_items)
        elif header_location == 'left':
            self._row_count = len(header_items)
            self._column_count = len(model_items) + 1
            self._transposed = True
            items.extend(header_items)
            for row in model_items:
                items.extend(row)
        elif header_location == 'right':
            self._row_count = len(header_items)
            self._column_count = len(model_items) + 1
            self._transposed = True
            for row in model_items:
                items.extend(row)
            items.extend(header_items)
        else:
            raise ValueError("Invalid header location '%s'" % header_location)

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    def row_count(self):
        """ Get the number of rows in the model.

        Returns
        -------
        result : int
            The number of rows in the model.

        """
        return self._row_count

    def column_count(self):
        """ Get the number of columns in the model.

        Returns
        -------
        result : int
            The number of columns in the model.

        """
        return self._column_count

    def item_flags(self, row, column):
        """ Get the item flags for the given indices.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        Returns
        -------
        result : int
            An or'd combination of ItemFlag enum values for the given
            indices.

        """
        if self._transposed:
            offset = column * self._row_count + row
        else:
            offset = row * self._column_count + column
        item = self._items[offset]
        if item is not None:
            return item.flags
        return ItemFlag.NO_ITEM_FLAGS

    def item_data(self, row, column, role):
        """ Get the item data for the given indices and role.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        role : int
            One of the ItemDataRole enum values.

        Returns
        -------
        result : object or None
            The data value for the given indices and role, or None if
            no data is available.

        """
        if self._transposed:
            offset = column * self._row_count + row
        else:
            offset = row * self._column_count + column
        item = self._items[offset]
        if item is not None:
            return getattr(self, self.role_handlers[role])(item)

    def set_item_data(self, row, column, value, role):
        """ Set the item data for the given indices and role.

        Parameters
        ----------
        row : int
            The row index of the item.

        column : int
            The column index of the item.

        value : object
            The value entered by the user.

        role : int
            One of the ItemDataRole enum values.

        Returns
        -------
        result : bool
            True if the item was set successfully, False otherwise.

        """
        if self._transposed:
            offset = column * self._row_count + row
        else:
            offset = row * self._column_count + column
        item = self._items[offset]
        if item is not None:
            handler = getattr(self, '_set' + self.role_handlers[role], None)
            if handler is not None:
                return handler(item, value)
        return False

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _item_display(self, item):
        """ Get the data for item display role.

        """
        return item.data

    def _item_decoration(self, item):
        """ Get the data for the item decoration role.

        """
        return item.icon_source

    def _item_edit(self, item):
        """ Get the data for the item edit role.

        """
        return item.edit_data

    def _item_tool_tip(self, item):
        """ Get the data for the item tool tip role.

        """
        return item.tool_tip

    def _item_status_tip(self, item):
        """ Get the data for the item status tip role.

        """
        return item.status_tip

    def _item_font(self, item):
        """ Get the data for the item font role.

        """
        font = item.font
        if not font:
            font = item.parent.font
        return font

    def _item_text_alignment(self, item):
        """ Get the data for the item text alignment role.

        """
        return item.text_alignment

    def _item_background(self, item):
        """ Get the data for the item background role.

        """
        background = item.background
        if not background:
            background = item.parent.background
        return background

    def _item_foreground(self, item):
        """ Get the data for the item foreground role.

        """
        foreground = item.foreground
        if not foreground:
            foreground = item.parent.foreground
        return foreground

    def _item_check_state(self, item):
        """ Get the data for the item check state role.

        """
        return item.check_state

    def _item_size_hint(self, item):
        """ Get the data for the item size hint role.

        """
        return item.size_hint

    def _item_edit_widget(self, item):
        """ Get the data for the item edit widget role.

        """
        return item.edit_widget

    def _set_item_edit(self, item, value):
        """ Get the data for the item edit role.

        """
        item.edit_data = value
        return True

    def _set_item_check_state(self, item, value):
        """ Get the data for the item check state role.

        """
        item.check_state = value
        return True

