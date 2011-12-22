#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------

from contextlib import contextmanager

from traits.api import Bool, List, Int, on_trait_change

from .base_selection_model import BaseSelectionModel


@contextmanager
def updating_trait(obj, trait, new=True):
    """ Context manager that sets a given trait to True before the with block
    and then back to its original value afterwards.

    """
    old = getattr(obj, trait)
    setattr(obj, trait, new)
    try:
        yield
    finally:
        setattr(obj, trait, old)


class RowSelectionModel(BaseSelectionModel):
    """ A selection model that maps to a list of row indices.

    Generally, this should be used with `selection_behavior='rows'`.

    """

    #: The selected row indices.
    selected_rows = List(Int)

    #: Whether we are currently updating the selected_rows trait to avoid cycles.
    _updating_selected_rows = Bool(False)


    @on_trait_change('selection_event')
    def _update_rows(self, event):
        selected_rows = []
        for topleft, botright in self.get_selection():
            selected_rows.extend(range(topleft.row, botright.row+1))
        selected_rows.sort()
        with updating_trait(self, '_updating_selected_rows'):
            self.selected_rows = selected_rows

    @on_trait_change('selected_rows,selected_rows_items')
    def _update_selection(self):
        if self._updating_selected_rows:
            return
        item_model = self.parent.item_model
        selection = []
        # FIXME: try to merge contiguous rows into ranges.
        for i in self.selected_rows:
            topleft = item_model.create_index(i, 0, item_model)
            botright = item_model.create_index(i, 0, item_model)
            selection.append((topleft, botright))
        self.set_selection(selection, ('clear_select', 'rows'))



