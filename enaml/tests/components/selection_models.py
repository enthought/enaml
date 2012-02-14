#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .enaml_test_case import EnamlTestCase, required_method


class SelectionTestHelper(object):
    """ Helper mixin for selection model test cases.

    """
    @property
    def widget(self):
        """ Get the current toolkit "widget", as it may change.

        """
        return self.component.abstract_obj.selection_model

    def index(self, row, column):
        """ Create an appropriate ModelIndex.

        """
        return self.item_model.create_index(row, column, self.item_model)

    def to_enaml_selection(self, pysel):
        """ Convert a selection list given with (row, col) tuples to a 
        selection list with ModexIndexes.

        """
        esel = []
        for topleft, botright in pysel:
            esel.append((self.index(*topleft), self.index(*botright)))
        return esel

    def from_enaml_selection(self, esel):
        """ Convert an Enaml selection list with ModelIndexes to one 
        given with (row, col) tuples for comparison purposes.

        """
        pysel = []
        for topleft, botright in esel:
            pysel.append(((topleft.row, topleft.column), 
                          (botright.row, botright.column)))
        return pysel

    def set_py_selection(self, pysel, command):
        """ Set the selection using (int, int) indices.

        """
        esel = self.to_enaml_selection(pysel)
        self.component.set_selection(esel, command)

    def get_py_selection(self):
        """ Get the selection using (int, int) indices.

        """
        return self.from_enaml_selection(self.component.get_selection())

    #--------------------------------------------------------------------------
    # Abstract methods
    #--------------------------------------------------------------------------
    @required_method
    def get_tk_selection(self, widget):
        """ Return the widget's selection as a list of (topleft, botright)
        ranges with (row, col) indexes.

        """
        pass


class TestBaseSelectionModel(EnamlTestCase, SelectionTestHelper):
    """ Logic for testing selection models.

    """
    def setUp(self):
        """ Set up tests for Enaml's BaseSelectionModel.

        """
        enaml_source = """
from enaml.item_models.standard_models import TableModel
import numpy as np

nrows = 20
ncols = 10

table = np.arange(nrows * ncols).reshape((nrows, ncols))
the_item_model = TableModel(table)

enamldef MainView(MainWindow):
    attr events
    TableView:
        name = 'table_view'
        item_model = the_item_model
        BaseSelectionModel:
            name = 'selection_model'
"""

        self.events = []
        self.view = self.parse_and_create(enaml_source, events=self.events)
        self.table_view = self.component_by_name(self.view, 'table_view')
        self.component = self.table_view.selection_model
        self.item_model = self.table_view.item_model

    def test_empty_initial_selection(self):
        """ No selection.

        """
        self.assertEqual(self.get_tk_selection(self.widget), [])
        self.assertEqual(self.get_py_selection(), [])

    def test_set_selection_clear_select(self):
        """ Test the 'clear_select' command.

        """
        pysel = [((1, 2), (3, 4))]
        self.set_py_selection(pysel, 'clear_select')
        self.assertEqual(self.get_tk_selection(self.widget), pysel)
        self.assertEqual(self.get_py_selection(), pysel)

        pysel = [((0, 1), (6,7))]
        self.set_py_selection(pysel, 'clear_select')
        self.assertEqual(self.get_tk_selection(self.widget), pysel)
        self.assertEqual(self.get_py_selection(), pysel)

        self.component.clear()
        self.assertEqual(self.get_tk_selection(self.widget), [])
        self.assertEqual(self.get_py_selection(), [])

    def test_set_selection_clear_select_rows(self):
        """ Test the ('clear_select', 'rows') command.

        """
        pysel = [((1, 2), (3, 4))]
        test_sel = [((1, 0), (3, 9))]
        self.set_py_selection(pysel, ('clear_select', 'rows'))
        self.assertEqual(self.get_tk_selection(self.widget), test_sel)
        self.assertEqual(self.get_py_selection(), test_sel)

    def test_set_selection_no_update(self):
        """ Test the 'no_update' command.

        """
        pysel = [((1, 2), (3, 4))]
        self.set_py_selection(pysel, 'no_update')
        self.assertEqual(self.get_tk_selection(self.widget), [])
        self.assertEqual(self.get_py_selection(), [])

        new = [((0, 1), (6, 7))]
        self.set_py_selection(new, 'clear_select')
        self.assertEqual(self.get_tk_selection(self.widget), new)
        self.assertEqual(self.get_py_selection(), new)

        self.set_py_selection(pysel, 'no_update')
        self.assertEqual(self.get_tk_selection(self.widget), new)
        self.assertEqual(self.get_py_selection(), new)

    def test_set_selection_select(self):
        """ Test the 'select' command.

        """
        pysel = [((1, 2), (3, 4))]
        self.set_py_selection(pysel, 'select')
        self.assertEqual(self.get_tk_selection(self.widget), pysel)
        self.assertEqual(self.get_py_selection(), pysel)

        new = [((5, 1), (7, 5))]
        self.set_py_selection(new, 'select')
        self.assertEqual(self.get_tk_selection(self.widget), pysel+new)
        self.assertEqual(self.get_py_selection(), pysel+new)

    def test_set_selection_deselect(self):
        """ Test the 'deselect' command.

        """
        pysel = [((1, 2), (3, 4))]
        self.set_py_selection(pysel, 'clear_select')
        self.assertEqual(self.get_tk_selection(self.widget), pysel)
        self.assertEqual(self.get_py_selection(), pysel)

        new = [((2, 2), (4, 4))]
        remainder = [((1,2), (1,4))]
        self.set_py_selection(new, 'deselect')
        self.assertEqual(self.get_tk_selection(self.widget), remainder)
        self.assertEqual(self.get_py_selection(), remainder)

    def test_set_selection_toggle(self):
        """ Test the 'toggle' command.

        """
        pysel = [((1, 2), (3, 4))]
        self.set_py_selection(pysel, 'clear_select')
        self.assertEqual(self.get_tk_selection(self.widget), pysel)
        self.assertEqual(self.get_py_selection(), pysel)

        new = [((2, 2), (4, 4))]
        remainder = [((1, 2), (1, 4)), ((4, 2), (4, 4))]
        self.set_py_selection(new, 'toggle')
        self.assertEqual(self.get_tk_selection(self.widget), remainder)
        self.assertEqual(self.get_py_selection(), remainder)


class TestRowSelectionModel(EnamlTestCase, SelectionTestHelper):
    """ Logic for testing RowSelectionModel

    """
    def setUp(self):
        """ Set up tests for Enaml's RowSelectionModel

        """
        enaml_source = """
from enaml.item_models.standard_models import TableModel
import numpy as np

nrows = 20
ncols = 10

table = np.arange(nrows * ncols).reshape((nrows, ncols))
the_item_model = TableModel(table)


enamldef MainView(MainWindow):
    attr events
    TableView:
        name = 'table_view'
        item_model = the_item_model
        RowSelectionModel:
            name = 'selection_model'
"""

        self.events = []
        self.view = self.parse_and_create(enaml_source, events=self.events)
        self.table_view = self.component_by_name(self.view, 'table_view')
        self.component = self.table_view.selection_model
        self.item_model = self.table_view.item_model

    def test_set_selected_rows(self):
        """ Test the selection of rows through the selected_rows trait.

        """
        self.assertEqual(self.component.selected_rows, [])
        self.component.selected_rows = [2, 3, 5, 6]
        pysel = [((2, 0), (2, 9)), ((3, 0), (3, 9)), ((5, 0), (5, 9)), ((6, 0), (6, 9))]
        self.assertEqual(self.get_tk_selection(self.widget), pysel)
        self.assertEqual(self.get_py_selection(), pysel)

        self.component.selected_rows.append(7)
        new = pysel + [((7, 0), (7, 9))]
        self.assertEqual(self.get_tk_selection(self.widget), new)
        self.assertEqual(self.get_py_selection(), new)

        del self.component.selected_rows[1]
        del new[1]
        self.assertEqual(self.get_tk_selection(self.widget), new)
        self.assertEqual(self.get_py_selection(), new)

    def test_get_selected_rows(self):
        """ Test that the selected_rows trait gets updated correctly when the
        selection is set elsewhere.

        """
        pysel = [((2, 0), (2, 9)), ((3, 0), (3, 9)), ((5, 0), (5, 9)), ((6, 0), (6, 9))]
        self.set_py_selection(pysel, ('clear_select', 'rows'))
        self.assertEqual(self.component.selected_rows, [2, 3, 5, 6])

