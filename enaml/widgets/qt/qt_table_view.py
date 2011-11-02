#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore
from .qt_control import QtControl

from ..table_view import AbstractTkTableView

from ...item_models.abstract_item_model import AbstractItemModel, ModelIndex
from .enums import QtOrientation, EnamlOrientation, EnamlDataRole


# XXX we need to add more handler support for the different modes of
# resetting the grid.
class AbstractItemModelTable(QtCore.QAbstractTableModel):

    def __init__(self, item_model):
        super(AbstractItemModelTable, self).__init__()
        if not isinstance(item_model, AbstractItemModel):
            raise TypeError('Model must be an instance of AbstractItemModel.')
        self._item_model = item_model
        self._item_model.on_trait_change(self._model_reset, 'model_reset')
        self._item_model.on_trait_change(self._model_about_to_be_reset, 'model_about_to_be_reset')
        self._item_model.on_trait_change(self._data_changed, 'data_changed')
        self._item_model.on_trait_change(self._header_data_changed, 'header_data_changed')

    def _model_about_to_be_reset(self):
        self.modelAboutToBeReset.emit()

    def _model_reset(self):
        self.modelReset.emit()

    def _data_changed(self, event):
        top_left = QtCore.QModelIndex(*event)
        bottom_right = QtCore.QModelIndex(*event)
        self.dataChanged(top_left, bottom_right)

    def _header_data_changed(self, event):
        orientation, first, last = event
        self.dataChanged(QtOrientation[orientation], first, last)

    def rowCount(self, parent):
        return self._item_model.row_count()

    def columnCount(self, parent):
        return self._item_model.column_count()

    def data(self, index, role, parent_index=ModelIndex()):
        model = self._item_model
        index = model.index(index.row(), index.column(), parent_index)
        data = model.data(index, EnamlDataRole[role])

        # adapt Enaml data values to Qt data values where appropriate
        if role == QtCore.Qt.BackgroundRole or role == QtCore.Qt.ForegroundRole:
            if data is not None:
                data = None#QColor_form_color(data)
        return data

    def headerData(self, section, orientation, role):
        model = self._item_model
        return model.header_data(section, EnamlOrientation[orientation], EnamlDataRole[role])


class QtTableView(QtControl, AbstractTkTableView):
    """ A Qt implementation of TableView.

    See Also
    --------
    TableView

    """
    #: The underlying model.
    model_wrapper = None

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Create the underlying QTableView control.

        """
        self.widget = QtGui.QTableView()

    def initialize(self):
        """ Initialize the widget with the attributes of this instance.

        """
        super(QtTableView, self).initialize()
        self.set_table_model(self.shell_obj.item_model)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_item_model_changed(self, item_model):
        """ The change handler for the 'item_model' attribute.

        """
        self.set_table_model(item_model)

    def set_table_model(self, model):
        """ Set the table view's model.

        """
        model_wrapper = AbstractItemModelTable(model)
        self.widget.setModel(model_wrapper)
        self.model_wrapper = model_wrapper

