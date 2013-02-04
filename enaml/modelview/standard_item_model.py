#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from collections import defaultdict
from weakref import ref

from traits.api import List, Callable, Enum, Instance, Uninitialized

from .abstract_models import AbstractItemModel
from .enums import ItemDataRole, ItemFlag
from .header_group import HeaderGroup
from .model_editor import ModelEditor
from .model_providers import ItemModelProvider


# TODO: Move the HeaderGroup, HeaderItem, ModelEditor, and EditGroup
# classes into this file. They are closely related, and properly
# handling dynamism can be done more efficiently if those classes
# can assume to be parented by a standard item model.


#: Use blist if available; it allows O(log(n)) random inserts and much
#: faster splicing for large lists.
try:
    from blist import blist
    list_class = blist
except ImportError:
    list_class = list


#------------------------------------------------------------------------------
# Offset Handling
#------------------------------------------------------------------------------
def _top_offset(model, row, column):
    """ Compute an item offset for a model with headers at the top.

    """
    return row * model._column_count + column


def _bottom_offset(model, row, column):
    """ Compute an item offset for a model with headers at the bottom.

    """
    row += 1
    if row == model._row_count:
        row = 0
    return row * model._column_count + column


def _left_offset(model, row, column):
    """ Compute an item offset for a model with headers at the left.

    """
    return column * model._row_count + row


def _right_offset(model, row, column):
    """ Compute an item offset for a model with headers at the right.

    """
    column += 1
    if column == model._column_count:
        column = 0
    return column * model._row_count + row


def _top_offset_inverse(model, index):
    """ Compute the offset inverse for a model with top headers.

    """
    return divmod(index, model._column_count)


def _bottom_offset_inverse(model, index):
    """ Compute the offset inverse for a model with bottom headers.

    """
    row, column = divmod(index, model._column_count)
    if row == 0:
        row = model._row_count
    row -= 1
    return (row, column)


def _left_offset_inverse(model, index):
    """ Compute the offset inverse for a model with left headers.

    """
    column, row = divmod(index, model._row_count)
    return (row, column)


def _right_offset_inverse(model, index):
    """ Compute the offset inverse for a model with right headers.

    """
    column, row = divmod(index, model._row_count)
    if column == 0:
        column = model._column_count
    column -= 1
    return (row, column)


_OFFSET_HANDLERS = {
    'top': _top_offset,
    'bottom': _bottom_offset,
    'left': _left_offset,
    'right': _right_offset,
}


_OFFSET_INVERSE_HANDLERS = {
    'top': _top_offset_inverse,
    'bottom': _bottom_offset_inverse,
    'left': _left_offset_inverse,
    'right': _right_offset_inverse,
}


#------------------------------------------------------------------------------
# Item Changed Notifier
#------------------------------------------------------------------------------
class ItemChangeNotifier(object):
    """ A lightweight trait notifier used by `StandardItemModelImpl`.

    An instance of this class is used by each instance of a standard
    item model to capture all trait changes on an instance of `Item`.
    This provides a much more memory efficient notification pattern for
    item changes requiring only O(n) space instead of O(m * n) and with
    a much smaller constant coefficient.

    """
    def __init__(self, model):
        """ Initialize an ItemChangeNotifier.

        Parameters
        ----------
        model : StandardItemModelImpl
            The standard item model which owns this notifier. Only a
            weakref is maintained to the notifier.

        """
        self._modelref = ref(model)

    def __call__(self, item, name, old, new):
        """ Called by traits to dispatch the notifier.

        """
        if old is not Uninitialized:
            model = self._modelref()
            if model is not None:
                model._on_item_changed(item, name)

    def equals(self, other):
        """ Compares this notifier against another for equality.

        """
        return False


#------------------------------------------------------------------------------
# Standard Item Model Implementation
#------------------------------------------------------------------------------
_ITEM_CHANGE_ATTRS = set([
    'data', 'edit_data', 'tool_tip', 'status_tip', 'font', 'background',
    'foreground', 'icon_source', 'flags', 'text_alignment', 'check_state',
    'size_hint',
])


class StandardItemModelImpl(AbstractItemModel):
    """ A concrete implementation of AbstractItemModel.

    A `StandardItemModelImpl` is designed to be used with the classes
    `ModelEditor` and `HeaderGroup`. It uses these to create an `Item`
    instance for each cell in the model. This model calss is reasonably
    efficient for models with up to ~100k items.

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
        self._layed_out = False
        self._items = list_class()
        self._header_groups = list_class()
        self._model_editors = list_class()
        self._header_location = 'top'
        self._offset = _OFFSET_HANDLERS[self._header_location]
        self._item_notifier = ItemChangeNotifier(self)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def header_location(self):
        """ Get the location of the headers for the model.

        Returns
        -------
        result : str
            The location of the headers for the model. Will be one of
            'left', 'right', 'top', or 'bottom'.

        """
        return self._header_location

    def set_header_location(self, location):
        """ Set the location of the headers for the model.

        Parameters
        ----------
        location : str
            The location of the headers for the model. Must be one of
            'left', 'right', 'top', or 'bottom'.

        """
        if location not in _OFFSET_HANDLERS:
            raise ValueError("Invalid header location '%s'" % location)
        old_location = self._header_location
        if old_location == location:
            return
        self._header_location = location
        self._offset = _OFFSET_HANDLERS[location]
        if not self._layed_out:
            return
        row_count = self._row_count
        column_count = self._column_count
        if old_location == 'top' or old_location == 'bottom':
            if location == 'left' or location == 'right':
                self._row_count = column_count
                self._column_count = row_count
        else:
            if location == 'top' or location == 'bottom':
                self._row_count = column_count
                self._column_count = row_count
        self.model_changed.emit()

    def add_header_group(self, group):
        """ Add a header group to the model.

        If the model is already layed out, this will trigger a proper
        update.

        Parameters
        ----------
        group : HeaderGroup
            The header group to add to the model.

        """
        self.insert_header_group(len(self._header_groups), group)

    def insert_header_group(self, index, group):
        """ Insert a header group into the model.

        If the model is already layed out, this will trigger a proper
        update.

        Parameters
        ----------
        index : int
            The index at which to insert the group.

        group : HeaderGroup
            The header group to insert into the model.

        """
        assert isinstance(group, HeaderGroup)
        self._header_groups.insert(index, group)
        # XXX not sure about this!
        attrs = 'background, foreground, font'
        group.on_trait_change(self._on_header_group_changed, attrs)
        if self._layed_out:
            pass

    def add_model_editor(self, editor):
        """ Add a model editor to the model.

        If the model is already layed out, this will trigger a proper
        update.

        Parameters
        ----------
        editor : ModelEditor
            The model editor to add to the model.

        """
        self.insert_model_editor(len(self._model_editors), editor)

    def insert_model_editor(self, index, editor):
        """ Insert a model editor to the model.

        If the model is already layed out, this will trigger a proper
        update.

        Parameters
        ----------
        index : int
            The index at which to insert the model editor.

        editor : ModelEditor
            The model editor to insert into the model.

        """
        assert isinstance(editor, ModelEditor)
        self._model_editors.insert(index, editor)
        if self._layed_out:
            pass

    def layout(self):
        """ Layout the items in the model.

        This should be called once during initialization, after all of
        the header groups and model editors have been added. This will
        generate the necessary items and lay them out in a grid. The
        model will reflect a row and column count of zero until this
        method is called. Calling this method mutliple times will be
        a no-op.

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

        # Assemble the final items list. It is assembled row-major with
        # headers at the beginning. Offset functions determine how this
        # is represented in the ui.
        items = self._items = list_class()
        items.extend(header_items)
        for row in model_items:
            items.extend(row)

        # See the docstring of ItemChangeNotifier. This method of
        # hooking up a notifier is much more memory efficient than
        # using on_trait_change for each attribute of interest. The
        # cost here is O(n) lists with 1 item each, vs O(n * m) lists
        # with an independent notifier object in each. Each of these
        # notifiers has an instance dict and a weakref.
        notifier = self._item_notifier
        for index, item in enumerate(items):
            if item is not None:
                if item._index is not None:
                    # Item appears more than once in the model. This is
                    # not formally supported. When an item appears more
                    # than once in the list, only the first cell will be
                    # updated. In that case, the behavior is undefined.
                    continue
                item._index = index
                item._notifiers(1).append(notifier)

        # Choose the right offset function for the header location and
        # update the column and row count for that location.
        header_location = self._header_location
        if header_location == 'top':
            self._row_count = len(model_items) + 1
            self._column_count = len(header_items)
            self._offset = _top_offset
        elif header_location == 'bottom':
            self._row_count = len(model_items) + 1
            self._column_count = len(header_items)
            self._offset = _bottom_offset
        elif header_location == 'left':
            self._row_count = len(header_items)
            self._column_count = len(model_items) + 1
            self._offset = _left_offset
        elif header_location == 'right':
            self._row_count = len(header_items)
            self._column_count = len(model_items) + 1
            self._offset = _right_offset
        else:
            raise ValueError("Invalid header location '%s'" % header_location)
        self._layed_out = True

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
        offset = self._offset(self, row, column)
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
        offset = self._offset(self, row, column)
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
        offset = self._offset(self, row, column)
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

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def _on_item_changed(self, item, name):
        """ Handle the item changed notification.

        This is called by the ItemChangeNotifier for this model. If the
        attribute is of interest to the model, and the model has been
        layed out, then the `item_changed` signal will be emitted.

        """
        if self._layed_out and name in _ITEM_CHANGE_ATTRS:
            index = item._index
            if self._items[index] is not item:
                # The item has moved in the model. Update the index.
                index = self._items.index(item)
                item._index = index
            invert = _OFFSET_INVERSE_HANDLERS[self._header_location]
            row, column = invert(self, index)
            self.item_changed.emit(row, column)

    def _on_header_group_changed(self, group, name, old, new):
        """ Handle the header group changed notification.

        Since the styling for a header item involves inheriting from the
        header group, all of the group's header items are invalid. This
        handler emits the change for the group's items.

        """
        if self._layed_out:
            for item in group.items():
                self._on_item_changed(item, name)


#------------------------------------------------------------------------------
# Standard Item Model
#------------------------------------------------------------------------------
class StandardItemModel(ItemModelProvider):
    """ A concrete implementation of `ItemModelProvider`.

    This is a declarative class which is used to generate an instance
    of `StandardItemModelImpl`. User code should declare `HeaderGroup`
    children which define the view structure of model. The user models
    to be edited should be assigned to the `models` list along with
    an `editor_loader` callable which will create an instance of
    `ModelEditor` for each model in the list.

    """
    #: The location of the headers in the model.
    header_location = Enum('top', 'left', 'right', 'bottom')

    #: The list of models to add to the editor item model.
    models = List

    #: A callable which accepts a single argument, a model, and returns
    #: a ModelEditor to use for editing that model instance. The loader
    #: is responsible for initializing any top-level editor state, but
    #: should *not* call the editor's `initialize` method.
    editor_loader = Callable

    #: Private storage for the item model instance.
    _item_model = Instance(StandardItemModelImpl)

    def _header_location_changed(self, location):
        model = self._item_model
        if model is not None and self.is_active:
            model.set_header_location(location)

    def item_model(self):
        """ Create the editor item model for this factory.

        Returns
        -------
        result : StandardItemModelImpl
            An instance of StandardItemModelImpl for the current state
            of the object.

        """
        model = self._item_model
        if model is not None:
            return model
        editor_loader = self.editor_loader
        if editor_loader is None:
            raise ValueError('Cannot build model without an editor loader')
        item_model = self._item_model = StandardItemModelImpl()
        item_model.set_header_location(self.header_location)
        for group in self.header_groups():
            item_model.add_header_group(group)
        for model in self.models:
            editor = editor_loader(model)
            if editor is not None:
                editor.initialize()
                item_model.add_model_editor(editor)
        item_model.layout()
        return item_model

    def header_groups(self):
        """ Get the header groups defined on this factory.

        Returns
        -------
        result : generator
            A generator which will yield the children of the view which
            are instances of `Group`.

        """
        for child in self.children:
            if isinstance(child, HeaderGroup):
                yield child

