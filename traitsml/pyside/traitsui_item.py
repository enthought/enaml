from enthought.traits.api import DelegatesTo, Instance
from enthought.traits.ui.ui import UI

from PySide import QtGui

from .element import Element
from .mixins import GeneralWidgetMixin


class TraitsUIWidget(GeneralWidgetMixin, QtGui.QWidget):
    pass


class TraitsUIItem(Element):

    # The HasTraits object that will provide the traits ui view
    model = DelegatesTo('abstract_obj')

    # The traits view for editing the object. Optional.
    view = DelegatesTo('abstract_obj')

    # The handler for editing the object. Optional.
    handler = DelegatesTo('abstract_obj')
    
    # The UI instance for the view we are embedding.
    item_ui = Instance(UI)
    
    def create_widget(self):
        return TraitsUIWidget()
    
    def init_layout(self):
        model = self.model
        view = self.view
        handler = self.handler
        widget = self.widget

        ui = model.edit_traits(parent=widget, view=view, 
                               handler=handler, kind='subpanel')

        self.item_ui = ui 
        
        # Remove an old layout if there is one
        old_layout = self.widget.layout()
        if old_layout is not None:
            old_layout.deleteLater()
            evt = QtCore.QEvent.DeferredDelete
            QtGui.QApplication.instance().sendPostedEvents(old_layout, evt)
            del old_layout

        layout = QtGui.QVBoxLayout()
        layout.addWidget(ui.control)
        self.widget.setLayout(layout)
        layout.activate()

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def _model_changed(self):
        self.layout_children()

    def _view_changed(self):
        self.layout_children()

    def _handler_changed(self):
        self.layout_children()


