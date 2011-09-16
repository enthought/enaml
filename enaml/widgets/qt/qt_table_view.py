from .qt import QtGui, QtCore

from traits.api import implements, Instance

from .qt_control import QtControl
from .styling import QColor_form_color

from ..table_view import ITableViewImpl

from ...item_models.abstract_item_model import AbstractItemModel, ModelIndex
from .enums import QtDataRole, QtOrientation, EnamlOrientation, EnamlDataRole

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
        top_left = QModelIndex(*event)
        bottom_right = QModelIndex(*event)
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
            data = QColor_form_color(data)
        return data

    def headerData(self, section, orientation, role):
        model = self._item_model
        return model.header_data(section, EnamlOrientation[orientation], EnamlDataRole[role])


class QtTableView(QtControl):

    implements(ITableViewImpl)

    model_wrapper = Instance(AbstractItemModelTable)

    #---------------------------------------------------------------------------
    # ITableViewImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        self.widget = QtGui.QTableView()

    def initialize_widget(self):
        self.set_table_model(self.parent.item_model)

    def create_style_handler(self):
        pass
    
    def initialize_style(self):
        style = self.parent.style
        min_width = style.get_property("min_width")
        min_height = style.get_property("min_height")

        if isinstance(min_width, int) and min_width >= 0:
            self.widget.setMinimumWidth(min_width)

        if isinstance(min_height, int) and min_height >= 0:
            self.widget.setMinimumHeight(min_height)


    def parent_item_model_changed(self, item_model):
        self.set_table_model(item_model)
        
    #---------------------------------------------------------------------------
    # implementation
    #---------------------------------------------------------------------------
    def set_table_model(self, model):
        model_wrapper = AbstractItemModelTable(model)
        self.widget.setModel(model_wrapper)
        self.model_wrapper = model_wrapper

