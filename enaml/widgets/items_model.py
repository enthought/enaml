#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from collections import defaultdict


#: Use blist if available; it allows O(log(n)) random inserts.
try:
    from blist import blist
    list_class = blist
except ImportError:
    list_class = list


class AbstractItemsModel(object):
    """ An abstract base class for defining items models.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def item_count(self):
        """ Get the number of items in the model.

        Returns
        -------
        result : int
            The number of items in the model.

        """
        raise NotImplementedError

    @abstractmethod
    def model_count(self):
        """ Get the number of models in the model.

        Returns
        -------
        result : int
            The number of models in the model.

        """
        raise NotImplementedError

    @abstractmethod
    def group(self, item_index):
        """ Get the group for the given item index.

        Parameters
        ----------
        item_index : int
            The index of the item in the model.

        Returns
        -------
        result : Group
            The group instance associated with the item index.

        """
        raise NotImplementedError

    @abstractmethod
    def item(self, item_index):
        """ Get the item for the given item index.

        Parameters
        ----------
        item_index : int
            The index of the item in the model.

        Returns
        -------
        result : Item
            The item instance for the given item index.

        """
        raise NotImplementedError

    @abstractmethod
    def editor(self, item_index, model_index):
        """ Get the editor for the given indices.

        Parameters
        ----------
        item_index : int
            The index of the item in the model.

        model_index : int
            The index of the model in the model.

        Returns
        -------
        result : ItemEdit or None
            The item edit instance for the associated item and model,
            or None if there is no editor available.

        """
        raise NotImplementedError


class ItemsModel(AbstractItemsModel):
    """ A concrete implementation of AbstractItemsModel.

    This is the standard implementation used by `ItemsView` as the
    default if a model is not explicitly provided by the user.

    """
    def __init__(self):
        """ Initialize an ItemsModel.

        """
        self._items = list_class()
        self._models = list_class()
        self._editors = None  # Created during `layout`.

    #--------------------------------------------------------------------------
    # Abstract API implementation
    #--------------------------------------------------------------------------
    def item_count(self):
        """ Get the number of items in the model.

        Returns
        -------
        result : int
            The number of items in the model.

        """
        return len(self._items)

    def model_count(self):
        """ Get the number of models in the model.

        Returns
        -------
        result : int
            The number of models in the model.

        """
        return len(self._models)

    def group(self, item_index):
        """ Get the group for the given item index.

        Parameters
        ----------
        item_index : int
            The index of the item in the model.

        Returns
        -------
        result : Group
            The group instance associated with the item index.

        """
        item = self._items[item_index]
        return item.parent

    def item(self, item_index):
        """ Get the item for the given item index.

        Parameters
        ----------
        item_index : int
            The index of the item in the model.

        Returns
        -------
        result : Item
            The item instance for the given item index.

        """
        return self._items[item_index]

    def editor(self, item_index, model_index):
        """ Get the editor for the given indices.

        Parameters
        ----------
        item_index : int
            The index of the item in the model.

        model_index : int
            The index of the model in the model.

        Returns
        -------
        result : ItemEdit
            The item edit instance for the associated item and model.

        """
        offset = model_index * len(self._items) + item_index
        return self._editors[offset]

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def add_group(self, group):
        """ Add a group to the model.

        The items of the group will be automatically extracted.

        Parameters
        ----------
        group : Group
            The group to add to the model.

        """
        self._items.extend(group.items())

    def add_model_editor(self, editor):
        """ Add a model editor to the model.

        Parameters
        ----------
        editor : ModelEditor
            The model editor which provides the editors for a model.

        """
        self._models.append(editor)

    def layout(self):
        """ Layout the model.

        This method will regenerate the internate layout of editors in
        the model. The model will be invalid until this method is called.

        """
        items = self._items
        editors = self._editors = list_class()
        for model in self._models:
            edit_groups = defaultdict(list)
            for edit_group in model.edit_groups():
                edit_groups[edit_group.name].append(edit_group)
            edit_cache = {}
            for item in items:
                group_name = item.parent.name
                if group_name not in edit_groups:
                    editors.append(None)
                    continue
                if group_name not in edit_cache:
                    item_editors = edit_cache[group_name] = {}
                    for group in edit_groups[group_name]:
                        # Collision resolution: last editor with the
                        # matchin name wins.
                        for item_editor in group.item_editors():
                            item_editors[item_editor.name] = item_editor
                else:
                    item_editors = edit_cache[group_name]
                item_name = item.name
                if item_name in item_editors:
                    editors.append(item_editors[item_name])
                else:
                    editors.append(None)

