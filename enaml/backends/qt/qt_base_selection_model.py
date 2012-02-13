#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_component import QtComponent

from ..base_selection_model import AbstractTkBaseSelectionModel


_SELECTION_MODE_MAP = {
    'single': QtGui.QAbstractItemView.SingleSelection,
    'contiguous': QtGui.QAbstractItemView.ContiguousSelection,
    'extended': QtGui.QAbstractItemView.ExtendedSelection,
    'multi': QtGui.QAbstractItemView.MultiSelection,
    'none': QtGui.QAbstractItemView.NoSelection,
}


_SELECTION_BEHAVIOR_MAP = {
    'items' : QtGui.QAbstractItemView.SelectItems,
    'rows' : QtGui.QAbstractItemView.SelectRows,
    'columns' : QtGui.QAbstractItemView.SelectColumns,
}


_SELECTION_COMMAND_MAP = {
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


class QtBaseSelectionModel(QtComponent, AbstractTkBaseSelectionModel):
    """ Qt implementation of the BaseSelectionModel.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create a space for the underlying QItemSelectionModel.

        We don't want to actually get it yet, since it depends on the
        AbstractItemModel being set on the parent, which won't happen 
        until the initialize() step.

        """
        self.widget = None

    def initialize(self):
        """ Get the QItemSelectionModel.

        """
        super(QtBaseSelectionModel, self).initialize()
        shell = self.shell_obj
        self.set_selection_mode(shell.selection_mode)
        self.set_selection_behavior(shell.selection_behavior)

    def bind(self):
        """ Bind to events.

        """
        super(QtBaseSelectionModel, self).bind()
        parent = self.shell_obj.parent
        parent.on_trait_change(self.reset_for_new_model, 'item_model')
        selection_model = self.selection_model
        selection_model.currentChanged.connect(self._update_current)
        selection_model.selectionChanged.connect(self._update_selection)

    def reset_for_new_model(self):
        """ Reset the state for a new AbstractItemModel.

        """
        self.initialize()
        parent = self.shell_obj.parent
        handler = self.reset_for_new_model
        parent.on_trait_change(handler, 'item_model', remove=True)
        self.bind()

    @property
    def selection_model(self):
        """ Get the QItemSelectionModel for the parent widget.

        """
        shell = self.shell_obj
        qitem_selection_model = shell.parent.toolkit_widget.selectionModel()
        return qitem_selection_model

    @property
    def item_model(self):
        """ Get the AbstractItemModelWrapper for the corresponding item 
        model.

        """
        # FIXME: We must get it from the widget itself instead of the
        # QItemSelectionModel.model() member. There seems to be a bug 
        # in PySide causing segfaults on finalization otherwise.
        return self.shell_obj.parent.toolkit_widget.model()

    def py_selection_to_qt(self, selection):
        """ Converts a list of tuples of Enaml ModelIndex ranges into
        a QItemSelection.

        """
        qsel = QtGui.QItemSelection()
        qitem_model = self.item_model
        for topleft, botright in selection:
            qtopleft = qitem_model.to_q_index(topleft)
            qbotright = qitem_model.to_q_index(botright)
            qsel.select(qtopleft, qbotright)
        return qsel

    def qt_selection_to_py(self, qselection):
        """ Converts a QItemSelection into a list of tuples of Enaml
        ModelIndex ranges.

        """
        pysel = []
        qitem_model = self.item_model
        for qrange in qselection:
            topleft = qitem_model.from_q_index(qrange.topLeft())
            botright = qitem_model.from_q_index(qrange.bottomRight())
            pysel.append((topleft, botright))
        return pysel

    def _update_current(self, current, previous):
        qitem_model = self.item_model
        old = qitem_model.from_q_index(previous)
        new = qitem_model.from_q_index(current)
        self.shell_obj.current_event((old, new))

    def _update_selection(self, current, previous):
        old = self.qt_selection_to_py(previous)
        new = self.qt_selection_to_py(current)
        self.shell_obj.selection_event((old, new))

    def clear(self):
        """ Clear the selection and the current index.

        """
        self.selection_model.clear()

    def get_current_index(self):
        """ Return the current ModelIndex or None if there is not one.

        """
        qindex = self.selection_model.currentIndex()
        index = self.item_model.from_q_index(qindex)
        return index

    def set_current_index(self, index):
        """ Set the current ModelIndex.

        """
        qindex = self.item_model.to_q_index(index)
        self.selection_model.setCurrentIndex(qindex)

    def set_selection(self, selection, command='clear_select'):
        """ Set the current selection.

        """
        if isinstance(command, basestring):
            command = (command,)
        qflag = 0
        for cmd in command:
            qflag |= _SELECTION_COMMAND_MAP[cmd]
        qsel = self.py_selection_to_qt(selection)
        self.selection_model.select(qsel, qflag)

    def get_selection(self):
        """ Get the current selection.

        """
        qsel = self.selection_model.selection()
        pysel = self.qt_selection_to_py(qsel)
        return pysel

    def set_selection_mode(self, selection_mode):
        """ Sets the selection mode.

        """
        shell = self.shell_obj
        behavior = _SELECTION_MODE_MAP[selection_mode]
        item_widget = shell.parent.toolkit_widget
        item_widget.setSelectionMode(behavior)

    def set_selection_behavior(self, selection_behavior):
        """ Sets the selection behavior.

        """
        shell = self.shell_obj
        behavior = _SELECTION_BEHAVIOR_MAP[selection_behavior]
        item_widget = shell.parent.toolkit_widget
        item_widget.setSelectionBehavior(behavior)

    #--------------------------------------------------------------------------
    # Parent Class Overrides
    #--------------------------------------------------------------------------
    def disable_updates(self):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QItemSelection.

        """
        pass

    def enable_updates(self):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QItemSelection.

        """
        pass

    def set_enabled(self, enabled):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QItemSelection.

        """
        pass

    def set_visible(self, visible):
        """ Overridden parent class method. This is a no-op since the 
        operation does not apply to a QItemSelection.

        """
        pass

