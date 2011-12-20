#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------

from .qt import QtGui
from .qt_base_component import QtBaseComponent
from ..base_item_selection_model import AbstractTkBaseItemSelectionModel

_COMMAND_MAP = {
    'clear_select': QtGui.QItemSelectionModel.ClearAndSelect,
    'no_update': QtGui.QItemSelectionModel.NoUpdate,
    'clear': QtGui.QItemSelectionModel.Clear,
    'select': QtGui.QItemSelectionModel.Select,
    'deselect': QtGui.QItemSelectionModel.Deselect,
    'toggle': QtGui.QItemSelectionModel.Toggle,
    'current': QtGui.QItemSelectionModel.Current,
    'rows': QtGui.QItemSelectionModel.Rows,
    'columns': QtGui.QItemSelectionModel.Columns,
    'select_current': QtGui.QItemSelectionModel.SelectCurrent,
    'toggle_current': QtGui.QItemSelectionModel.ToggleCurrent,
}



class QtBaseItemSelectionModel(QtBaseComponent, AbstractTkBaseItemSelectionModel):
    """ Qt implementation of the BaseItemSelectionModel.

    """

    def create(self, parent):
        """ Create a space for the underlying QItemSelectionModel.

        We don't want to actually get it yet, since it depends on the
        AbstractItemModel being set on the parent, which won't happen until the
        initialize() step.

        """
        self.widget = None

    def initialize(self):
        """ Get the QItemSelectionModel.

        """
        super(QtBaseItemSelectionModel, self).initialize()
        self.widget = self.get_qitem_selection_model()

    def bind(self):
        """ Bind to events.

        """
        super(QtBaseItemSelectionModel, self).bind()
        #parent = self.shell_obj.parent
        #parent.on_trait_change(self.reset_for_new_model, 'item_model')
        self.widget.currentChanged.connect(self._update_current)
        self.widget.selectionChanged.connect(self._update_selection)

    def reset_for_new_model(self):
        """ Reset the state for a new AbstractItemModel.

        """
        self.initialize()
        #parent = self.shell_obj.parent
        #parent.on_trait_change(self.reset_for_new_model, 'item_model', remove=True)
        self.bind()

    def get_qitem_selection_model(self):
        """ Get the QItemSelectionModel for the parent widget.

        """
        shell = self.shell_obj
        qitem_selection_model = shell.parent.toolkit_widget.selectionModel()
        return qitem_selection_model

    def py_selection_to_qt(self, selection):
        """ Convert the Python list of ModelIndex ranges to a QItemSelection.

        """
        qsel = QtGui.QItemSelection()
        qitem_model = self.widget.model()
        for topleft, botright in selection:
            qtopleft = qitem_model.to_q_index(topleft)
            qbotright = qitem_model.to_q_index(botright)
            qsel.select(qtopleft, qbotright)
        return qsel

    def qt_selection_to_py(self, qselection):
        """ Convert a QItemSelection to a list of ModelIndex ranges.

        """
        pysel = []
        qitem_model = self.widget.model()
        for qrange in qselection:
            topleft = qitem_model.from_q_index(qrange.topLeft())
            botright = qitem_model.from_q_index(qrange.bottomRight())
            pysel.append((topleft, botright))
        return pysel

    def _update_current(self, current, previous):
        qitem_model = self.widget.model()
        old = qitem_model.from_q_index(previous)
        new = qitem_model.from_q_index(current)
        self.shell_obj.current_event = (old, new)

    def _update_selection(self, current, previous):
        old = self.qt_selection_to_py(previous)
        new = self.qt_selection_to_py(current)
        self.shell_obj.selection_event = (old, new)

    def clear(self):
        """ Clear the selection and the current index.

        """
        self.widget.clear()

    def get_current_index(self):
        """ Return the current ModelIndex or None if there is not one.

        """
        qindex = self.widget.currentIndex()
        qitem_model = self.widget.model()
        index = qitem_model.from_q_index(qindex)
        return index

    def set_current_index(self, index):
        """ Set the current ModelIndex.

        """
        item_model = self.widget.model()
        qindex = item_model.to_q_index(index)
        self.widget.setCurrentIndex(qindex)

    def set_selection(self, selection, command='clear_select'):
        """ Set the current selection.

        """
        if isinstance(command, basestring):
            command = (command,)
        qflag = 0
        for cmd in command:
            qflag |= _COMMAND_MAP[cmd]
        qsel = self.py_selection_to_qt(selection)
        self.widget.select(qsel, qflag)

    def get_selection(self):
        """ Get the current selection.

        """
        qsel = self.widget.selection()
        pysel = self.qt_selection_to_py(qsel)
        return pysel

