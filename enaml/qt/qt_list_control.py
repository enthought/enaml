#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QListWidget
from .qt_control import QtControl
from .qt_list_item import QtListItem


class QtListControl(QtControl):
    """ A Qt implementation of an Enaml ListControl.

    """
    def create_widget(self, parent, tree):
        return QListWidget(parent)

    def create(self, tree):
        super(QtListControl, self).create(tree)
        from .qt.QtGui import QFont
        f = QFont()
        f.setWeight(87)
        f.setPointSize(19)
        f.setFamily('Consolas')
        self.widget().setFont(f)
        self.set_items(tree['items'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_items(self, items):
        return
        qt_items = []
        session = self._session
        widget = self.widget()
        widget.clear()
        for tree in items:
            qt_items.append(QtListItem.construct(tree, self, session))
        #for qt_item in qt_items:
        #    widget.addItem(qt_item.widget())
        for qt_item in qt_items:
            qt_item.initialize()
        for qt_item in qt_items:
            qt_item.activate()

