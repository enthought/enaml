#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance

from enaml.widgets.control import Control

from .abstract_models import AbstractItemModel, NullItemModel
from .model_providers import ItemModelProvider


class ItemView(Control):
    """ A control for viewing a concrete instance of `AbstractItemModel`.

    """
    #: The item model to view with this control. If not provided, the
    #: children will be scanned for an instance of `ItemModelProvider`,
    #: and that object will be used to provide the item model.
    item_model = Instance(AbstractItemModel, factory=NullItemModel)

    #: By default, an ItemView expands freely in width and height.
    hug_width = 'ignore'
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def post_initialize(self):
        """ A post initialization handler.

        This handler will resolve the item model to use for the view.

        """
        super(ItemView, self).post_initialize()
        if isinstance(self.item_model, NullItemModel):
            provider = self.item_model_provider()
            if provider is not None:
                self.item_model = provider.item_model()

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

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def item_model_provider(self):
        """ Get the item model provider declared as child of this view.

        Returns
        -------
        result : ItemModelProvider or None
            The last child which is an instance of `ItemModelProvider`,
            or None if there is no such child.

        """
        provider = None
        for child in self.children:
            if isinstance(child, ItemModelProvider):
                provider = child
        return provider

