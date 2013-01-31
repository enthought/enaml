#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, List, Str, Callable, Instance

from enaml.core.declarative import Declarative

from .control import Control
from .items_model import AbstractItemsModel, ItemsModel


class Item(Declarative):
    """ A class for displaying an item in an `ItemsView`.

    When an `Item` is declared as the child of a Group, the `name`
    of the item is used to find a corresponding `ItemEditor` declared
    by the associated `ModelEditor`.

    """
    #: The background color of the item label. Supports CSS3 color
    #: strings. If not explicitly defined, it will be inherited from
    #: the parent Group.
    background = Str

    #: The foreground color of the item label. Supports CSS3 color
    #: strings. If not explicitly defined, it will be inherited from
    #: the parent Group.
    foreground = Str

    #: The font of the item label. Supports CSS3 font strings. If not
    #: explicitly defined, it will be inherited from the parent Group.
    font = Str

    #: Whether or not the item is visible in the view.
    visible = Bool(True)


class Group(Declarative):
    """ A class for displaying items in an `ItemsView`.

    When a `Group` is declared as a child of an `ItemsView`, the `name`
    of the group is used to find the correponding `EditGroup` instances
    declared by the associated `ModelEditor`.

    """
    #: The background color of the group header. Supports CSS3 color
    #: strings.
    background = Str

    #: The foreground color of the group header. Supports CSS3 color
    #: strings.
    foreground = Str

    #: The font of the group header.
    font = Str

    #: Whether or not the group is visible in the view.
    visible = Bool(True)

    def items(self):
        """ Get the items defined on this group.

        Returns
        -------
        result : generator
            A generator which will yield the children of the group
            which are instances of `Item`.

        """
        for child in self.children:
            if isinstance(child, Item):
                yield child


class ItemsView(Control):
    """ A control for rich editing a collection of models.

    An `ItemsView` uses `Group` children to define what to edit on
    the models and how that information should be arranged in the
    view. The children of the `ItemsView` define the *structure* of
    what is visible in the view.

    `ModelEditor` instances are used to define how each value on a
    model is respresented and edited. The model editors define the
    *content* of the view.

    """
    #: The list of models to show in the view.
    models = List

    #: A callable which accepts a single argument, a model, and returns
    #: an ItemEditor to use for editing that model instance. The loader
    #: is responsible for initializing any top-level editor state, but
    #: should *not* call the editor's `initialize` method.
    editor_loader = Callable

    #: An optional items model which can be supplied directly instead
    #: of having the view create one automatically from its children.
    #: If this is provided, then `models`, `editor_loader`, and the
    #: children of the view will all be ignored.
    items_model = Instance(AbstractItemsModel)

    hug_width = 'ignore'
    hug_height = 'ignore'

    def post_initialize(self):
        """

        """
        super(ItemsView, self).post_initialize()
        if self.items_model is None:
            self.set_guarded(items_model=self._build_model())

    def snapshot(self):
        """ Get the snapshot dictionary for the control.

        """
        snap = super(ItemsView, self).snapshot()
        snap['items_model'] = self.items_model
        return snap

    def bind(self):
        """ Bind the change handlers for the control.

        """
        super(ItemsView, self).bind()
        self.publish_attributes('items_model')

    def groups(self):
        """ Get the groups defined on this view.

        Returns
        -------
        result : generator
            A generator which will yield the children of the view which
            are instances of `Group`.

        """
        for child in self.children:
            if isinstance(child, Group):
                yield child

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _build_model(self):
        """ Generates an items model for the view.

        Returns
        -------
        result : ItemsModel
            An intialized and layed-out items model.

        """
        editor_loader = self.editor_loader
        if editor_loader is None:
            raise ValueError('Cannot build model without an editor loader')
        items_model = ItemsModel()
        for group in self.groups():
            items_model.add_group(group)
        for model in self.models:
            editor = editor_loader(model)
            if editor is not None:
                editor.initialize()
                items_model.add_model_editor(editor)
        items_model.layout()
        return items_model

