#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from collections import defaultdict

from traits.api import (
    List, Callable, Enum, Instance, Unicode, Property, Str, Bool, Any, Int,
    Uninitialized,
)

from enaml.core.declarative import Declarative, scope_lookup
from enaml.core.templated import Templated

from .abstract_models import AbstractItemModel
from .enums import ItemFlag, AlignmentFlag
from .item import Item, ItemListener
from .model_providers import ItemModelProvider
from .utils import SlotData, SlotDataProperty, slot_data_setter


#: Use blist if available; it allows O(log(n)) random inserts and much
#: faster splicing for large lists.
try:
    from blist import blist
    list_class = blist
except ImportError:
    list_class = list


#------------------------------------------------------------------------------
# Standard Item Model Implementation
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


class StandardItemModelImpl(AbstractItemModel):
    """ A concrete implementation of AbstractItemModel.

    A `StandardItemModelImpl` is designed to be used with the classes
    `ModelEditor` and `HeaderGroup`. It uses these to create an `Item`
    instance for each cell in the model. This model calss is reasonably
    efficient for models with up to ~100k items.

    """
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

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def has_items(self):
        """ Returns whether or not this model has items.

        Returns
        -------
        result : bool
            True if the model is layed and has a row and column count
            greater than zero.

        """
        r = self._layed_out and self._row_count > 0 and self._column_count > 0
        return r

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
            for header_item in header_group.header_items():
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
        for index, item in enumerate(items):
            if item is not None:
                if item._index is not None:
                    # Item appears more than once in the model. This is
                    # not formally supported. The behavior is undefined.
                    continue
                item._index = index

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
    # AbstractItemModel Interface
    #--------------------------------------------------------------------------
    def row_count(self):
        """ Get the number of rows in the model.

        See Also: `AbstractItemModel.row_count`

        """
        return self._row_count

    def column_count(self):
        """ Get the number of columns in the model.

        See Also: `AbstractItemModel.column_count`

        """
        return self._column_count

    def flags(self, row, column):
        """ Get the item flags for the given indices.

        See Also: `AbstractItemModel.flags`

        """
        offset = self._offset(self, row, column)
        item = self._items[offset]
        if item is not None:
            return item.flags
        return ItemFlag.NO_ITEM_FLAGS

    def data(self, row, column):
        """ Get the item data for the given indices.

        See Also: `AbstractItemModel.data`

        """
        offset = self._offset(self, row, column)
        item = self._items[offset]
        if item is not None:
            return item.data

    def edit_data(self, row, column):
        """ Get the item edit data for the given indices.

        See Also: `AbstractItemModel.edit_data`

        """
        offset = self._offset(self, row, column)
        item = self._items[offset]
        if item is not None:
            return item.edit_data

    def icon_source(self, row, column):
        """ Get the icon source for the given indices.

        See Also: `AbstractItemModel.icon_source`

        """
        offset = self._offset(self, row, column)
        item = self._items[offset]
        if item is not None:
            return item.icon_source

    def tool_tip(self, row, column):
        """ Get the tool tip for the given item indices.

        See Also: `AbstractItemModel.icon_source`

        """
        offset = self._offset(self, row, column)
        item = self._items[offset]
        if item is not None:
            return item.tool_tip

    def status_tip(self, row, column):
        """ Get the status tip for the given item indices.

        See Also: `AbstractItemModel.icon_source`

        """
        offset = self._offset(self, row, column)
        item = self._items[offset]
        if item is not None:
            return item.status_tip

    def font(self, row, column):
        """ Get the font for the given item indices.

        See Also: `AbstractItemModel.icon_source`

        """
        offset = self._offset(self, row, column)
        item = self._items[offset]
        if item is not None:
            font = item.font
            if not font:
                font = item.parent.font
            return font

    def background(self, row, column):
        """ Get the background color for the given item indices.

        See Also: `AbstractItemModel.icon_source`

        """
        offset = self._offset(self, row, column)
        item = self._items[offset]
        if item is not None:
            background = item.background
            if not background:
                background = item.parent.background
            return background

    def foreground(self, row, column):
        """ Get the foreground color for the given item indices.

        See Also: `AbstractItemModel.icon_source`

        """
        offset = self._offset(self, row, column)
        item = self._items[offset]
        if item is not None:
            foreground = item.foreground
            if not foreground:
                foreground = item.parent.foreground
            return foreground

    def text_alignment(self, row, column):
        """ Get the text alignment for the given indices.

        See Also: `AbstractItemModel.icon_source`

        """
        offset = self._offset(self, row, column)
        item = self._items[offset]
        if item is not None:
            return item.text_alignment
        return AlignmentFlag.ALIGN_CENTER

    def check_state(self, row, column):
        """ Get the check state for the given indices.

        See Also: `AbstractItemModel.icon_source`

        """
        offset = self._offset(self, row, column)
        item = self._items[offset]
        if item is not None:
            return item.check_state

    def size_hint(self, row, column):
        """ Get the size hint for the given indices.

        See Also: `AbstractItemModel.icon_source`

        """
        offset = self._offset(self, row, column)
        item = self._items[offset]
        if item is not None:
            return item.size_hint

    def set_data(self, row, column, value):
        """ Set the item data for the given indices.

        See Also: `AbstractItemModel.set_data`

        """
        offset = self._offset(self, row, column)
        item = self._items[offset]
        if item is not None:
            item.edit_data = value
            return True
        return False

    def set_check_state(self, row, column, value):
        """ Set the item check state for the given indices.

        See Also: `AbstractItemModel.set_check_state`

        """
        offset = self._offset(self, row, column)
        item = self._items[offset]
        if item is not None:
            item.check_state = value
            return True
        return False

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def on_item_changed(self, item, name):
        """ Handle the item changed notification.

        This method is called by the StandardItemModel instance which
        created the model when one of the items indicates that it has
        changed. This method will determine the (row, column) index of
        the effected item and emit the `data_changed` signal so that
        any attached UIs can update.

        """
        if self.has_items():
            index = item._index
            if index is None:
                return # Item was never added
            if self._items[index] is not item:
                index = self._items.index(item)
                item._index = index
            invert = _OFFSET_INVERSE_HANDLERS[self._header_location]
            row, column = invert(self, index)
            self.data_changed.emit(row, column)

    def on_header_group_changed(self, group, name):
        if self.has_items():
            invert = _OFFSET_INVERSE_HANDLERS[self._header_location]
            items = self._items
            for item in group.header_items():
                index = item._index
                if index is None:
                    continue
                if items[index] is not item:
                    index = items.index(item)
                    item._index = index
                row, column = invert(self, index)
                self.data_changed.emit(row, column)

    def on_header_item_changed(self, item, name):
        self.on_item_changed(item, name)

    def on_edit_group_changed(self, group, name):
        pass

    def on_edit_item_changed(self, item, name):
        self.on_item_changed(item, name)


#-----------------------------------------------------------------------------
# Standard Item Model Declarative Classes
#------------------------------------------------------------------------------
def _get_header_data(self):
    """ A custom property getter for a HeaderItem.

    This getter retrieves the data for the item, and if the data is not
    defined, it returns the name of the item instead.

    """
    value = self._slot_data.data
    if value is Uninitialized:
        value = self.name
    return value


class HeaderItem(Item):
    """ `HeaderItem` is one of the standard item model classes.

    A `HeaderItem` is an `Item` subclass which behaves like a header
    in the model. The `name` of the header item is used to locate the
    matching items on the model editors.

    Using a `HeaderItem` without a `HeaderGroup` parent is undefined.

    """
    #: By default, a header's data comes from its 'name' unless it is
    #: explicitly overridden by the user.
    data = Property(
        trait=Unicode, fget=_get_header_data, fset=slot_data_setter('data')
    )

    #: By default, a header item is enabled.
    flags = SlotDataProperty('flags', Int, default=ItemFlag.ITEM_IS_ENABLED)


class HeaderGroupData(SlotData):
    """ A SlotData subclass for storing header group data.

    """
    __slots__ = ('foreground', 'background', 'font')

    def notify(self, group, name):
        """ Handle the slot's change notification.

        This handler will forward the notification to its parent.

        """
        # group.parent is a StandardItemModel instance.
        group.parent.on_header_group_changed(group, name)


class HeaderGroup(Declarative):
    """ `HeaderGroup` is one of the standard item model classes.

    A `HeaderGroup` is used to collect `HeaderItem` children. The
    `name` of the header group is matched against the edit group
    children of the model editors to locate the relevant items for
    a model.

    Using a `HeaderGroup` without a `StandardItemModel` parent is
    undefined.

    """
    #: The background color of the header group. Supports CSS3 color
    #: strings.
    background = SlotDataProperty('background', Str)

    #: The foreground color of the header group. Supports CSS3 color
    #: strings.
    foreground = SlotDataProperty('foreground', Str)

    #: The font of the header group. Supports CSS3 shorthand font
    #: strings.
    font = SlotDataProperty('font', Str)

    #: The private slot data storage for the header group. This should
    #: not be manipulated by user code.
    _slot_data = Instance(HeaderGroupData, ())

    def header_items(self):
        """ Get the header items defined on this header group.

        Returns
        -------
        result : generator
            A generator which will yield the group children which are
            instances of `HeaderItem`.

        """
        for child in self.children:
            if isinstance(child, HeaderItem):
                yield child

    def on_item_changed(self, item, name):
        """ Handle the data changed notification from a child item.

        """
        self.parent.on_header_item_changed(item, name)


ItemListener.register(HeaderGroup)


class EditGroupData(SlotData):
    """ A SlotData subclass for storing edit group data.

    """
    __slots__ = ('foreground', 'background', 'font', '_built')

    def notify(self, group, name):
        """ Handle the slot's change notification.

        This handler will forward the change to notifier installed on
        the item.

        """
        # group.parent is a ModelEditor instance.
        group.parent.on_edit_group_changed(group, name)


class EditGroup(Templated):
    """ `EditGroup` is one of the standard item model classes.

    An `EditGroup` is used to collect `Item` children. The `name` of
    the edit group is matched against the corresponding header groups
    to determine which items to include in the item model.

    An `EditGroup` will delay the creation of its children until they
    are explicitly requested. This allows the underlying item model to
    be more efficient by only creating the items required for display.

    Children are created in an independent scope seeded with the scope
    of the editor group. Children created by one group will not have
    access to those created by another group.

    Using an `EditGroup` without a `ModelEditor` parent is undefined.

    """
    #: The background color of the editor group. Supports CSS3 color
    #: strings.
    background = SlotDataProperty('background', Str)

    #: The foreground color of the editor group. Supports CSS3 color
    #: strings.
    foreground = SlotDataProperty('foreground', Str)

    #: The font the editor group. Supports CSS3 shorthand font strings.
    font = SlotDataProperty('font', Str)

    #: A private flag indicating whether the children have been built.
    _built = SlotDataProperty('_built', Bool, notify=False, default=False)

    #: The private slot data storage for the header group. This should
    #: not be manipulated by user code.
    _slot_data = Instance(EditGroupData, ())

    def items(self):
        """ Get the items defined on this edit group.

        Returns
        -------
        result : generator
            A generator which will yield the group children which are
            instances of `Item`.

        """
        self._build_if_needed()
        for child in self.children:
            if isinstance(child, Item):
                yield child

    def on_item_changed(self, item, name):
        """ Handle the data changed notification from a child item.

        """
        self.parent.on_edit_item_changed(item, name)

    def _build_if_needed(self):
        """ Create and initialize the children if needed.

        This method will create and intialize the children of the group
        the first time it is called. Afterwards, it is no-op unless the
        private `_built` flag is reset to False.

        """
        if self._built:
            return
        self._built = True
        with self.children_event_context():
            for identifiers, f_globals, descriptions in self._templates:
                scope = identifiers.copy()
                for descr in descriptions:
                    cls = scope_lookup(descr['type'], f_globals, descr)
                    instance = cls(self)
                    with instance.children_event_context():
                        instance.populate(descr, scope, f_globals)
                    instance.initialize()


ItemListener.register(EditGroup)


class ModelEditor(Declarative):
    """ `ModelEditor` is one of the standard item model classes.

    A `ModelEditor` is used to collect `EditGroup` children. A model
    editor is created for each object in the list of `models` given
    to a `StandardItemModel`. The editor's edit groups determine which
    items are available to edit and display the data in the model.

    """
    #: The model object to edit with this editor. Subclasses may
    #: reimplement this trait as needed to customize behavior.
    model = Any

    def edit_groups(self):
        """ Get the edit groups defined on this model editor.

        Returns
        -------
        result : generator
            A generator which will yield the children of the editor
            which are instances of `EditGroup`.

        """
        for child in self.children:
            if isinstance(child, EditGroup):
                yield child

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def on_edit_group_changed(self, group, name):
        """ Handle the change notification from an edit group child.

        """
        self.parent.on_edit_group_changed(group, name)

    def on_edit_item_changed(self, item, name):
        self.parent.on_edit_item_changed(item, name)


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
        with self.children_event_context():
            for model in self.models:
                editor = editor_loader(model)
                if editor is not None:
                    editor.set_parent(self)
                    editor.initialize()
                    item_model.add_model_editor(editor)
        item_model.layout()
        return item_model

    def header_groups(self):
        """ Get the header groups defined on this object.

        Returns
        -------
        result : generator
            A generator which will yield the children of the object
            which are instances of `HeaderGroup`.

        """
        for child in self.children:
            if isinstance(child, HeaderGroup):
                yield child

    def model_editors(self):
        """ Get the model editors defined on this object.

        Returns
        -------
        result : generator
            A generator which will yield the children of the object
            which are instances of `ModelEditor`.

        """
        for child in self.children:
            if isinstance(child, ModelEditor):
                yield child

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def on_header_group_changed(self, group, name):
        """ A change notifier invoked by a child `HeaderGroup`.

        This method forwards the change on to the item model.

        """
        model = self._item_model
        if model is not None:
            model.on_header_group_changed(group, name)

    def on_header_item_changed(self, item, name):
        """ A change notifier invoked by a child `HeaderGroup`.

        The group forwards the change from a child header item. This
        method forwards the change to the item model.

        """
        model = self._item_model
        if model is not None:
            model.on_header_item_changed(item, name)

    def on_edit_group_changed(self, group, name):
        """ A change notifier invoked by a child `ModelEditor`.

        The model editor forwards the change from a child edit group.
        This method forwards the change to the item model.

        """
        model = self._item_model
        if model is not None:
            model.on_edit_group_changed(group, name)

    def on_edit_item_changed(self, item, name):
        """ A change notifier invoked by a child `ModelEditor`.

        The model editor forwards the change from a child edit group,
        which forwards it from a child item. This method forwards the
        change to the item model.

        """
        model = self._item_model
        if model is not None:
            model.on_edit_item_changed(item, name)

