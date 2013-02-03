#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
# Note: This file is imported as part of enaml.widgets.api so imports
# from enaml.modelview should be delayed until needed.
from traits.api import List, Callable, Instance

from .control import Control


class ItemView(Control):
    """ A control for rich editing a collection of models.

    An `ItemView` uses `HeaderGroup` children to define what to edit on
    the models and how that information should be arranged in the view.

    `ModelEditor` instances are used to define how each value on a model
    is respresented and edited.

    """
    #: The list of models to show in the view.
    models = List

    #: A callable which accepts a single argument, a model, and returns
    #: a ModelEditor to use for editing that model instance. The loader
    #: is responsible for initializing any top-level editor state, but
    #: should *not* call the editor's `initialize` method.
    editor_loader = Callable

    #: An optional item model which can be given to the view. If this
    #: is provided, the view will ignore its children and use this
    #: model. Otherwise, it will create its own `ItemModel` instance
    #: populated with the child header groups and the model editors.
    item_model = Instance('enaml.modelview.abstract_models.AbstractItemModel')

    #: By default, an ItemView expands freely in width and height.
    hug_width = 'ignore'
    hug_height = 'ignore'

    def post_initialize(self):
        """

        """
        super(ItemView, self).post_initialize()
        if self.item_model is None:
            self.set_guarded(item_model=self._build_item_model())

    def snapshot(self):
        """ Get the snapshot dictionary for the control.

        """
        snap = super(ItemView, self).snapshot()
        snap['item_model'] = self.item_model
        return snap

    def bind(self):
        """ Bind the change handlers for the control.

        """
        super(ItemView, self).bind()
        self.publish_attributes('item_model')

    def header_groups(self):
        """ Get the header groups defined on this view.

        Returns
        -------
        result : generator
            A generator which will yield the children of the view which
            are instances of `Group`.

        """
        from enaml.modelview.header_group import HeaderGroup
        for child in self.children:
            if isinstance(child, HeaderGroup):
                yield child

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _build_item_model(self):
        """ Generates an items model for the view.

        Returns
        -------
        result : ItemsModel
            An intialized and layed-out items model.

        """
        editor_loader = self.editor_loader
        if editor_loader is None:
            raise ValueError('Cannot build model without an editor loader')
        from enaml.modelview.item_model import ItemModel
        item_model = ItemModel()
        for group in self.header_groups():
            item_model.add_header_group(group)
        for model in self.models:
            editor = editor_loader(model)
            if editor is not None:
                editor.initialize()
                item_model.add_model_editor(editor)
        item_model.layout()
        return item_model

