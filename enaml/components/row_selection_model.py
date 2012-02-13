#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import List, Int, on_trait_change

from .base_selection_model import BaseSelectionModel

from ..guard import guard


class RowSelectionModel(BaseSelectionModel):
    """ A selection model that maps to a list of row indices.

    Generally, this should be used with `selection_behavior='rows'`.

    """
    #: The selected row indices.
    selected_rows = List(Int)

    #: Only select rows.
    selection_behavior = 'rows'

    @on_trait_change('selection_event')
    def _update_rows(self, event):
        selected_rows = []
        for topleft, botright in self.get_selection():
            selected_rows.extend(range(topleft.row, botright.row+1))
        selected_rows.sort()
        with guard(self, self._update_rows):
            self.selected_rows = selected_rows

    @on_trait_change('selected_rows,selected_rows_items')
    def _update_selection(self):
        if guard.guarded(self, self._update_rows):
            return
        item_model = self.parent.item_model
        selection = []
        # FIXME: try to merge contiguous rows into ranges.
        for i in self.selected_rows:
            topleft = item_model.create_index(i, 0, item_model)
            botright = item_model.create_index(i, 0, item_model)
            selection.append((topleft, botright))
        self.set_selection(selection, ('clear_select', 'rows'))

