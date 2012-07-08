#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------

""" An implementation of a popup widget with rounded corners and an arrow 
anchoring it to an underlying widget. Useful for transient dialogs.
"""
import sys
from enaml.qt.qt import QtGui
from enaml.qt.qt.q_popup_widget import QPopupWidget
from enaml.qt.qt.q_popup_tooltip import QPopupTooltip

if __name__ == "__main__":

    class Test(QtGui.QWidget):
        def __init__(self, parent=None):
            super(Test, self).__init__(parent)
            self.setWindowTitle('Test popup')
            
            layout = QtGui.QHBoxLayout()
            self.setLayout(layout)
            b1 = QtGui.QPushButton('Popup')
            b1.clicked.connect(self.showPopup)
            layout.addWidget(b1)

            b2 = QtGui.QPushButton('Tooltip')
            b2.clicked.connect(self.showTooltip)
            layout.addWidget(b2)

        def showPopup(self, checked=False):
            sender = self.sender()
            popup = QPopupWidget(sender)
            popup.setAnchor('bottom')
            popup.setRelativePos((0.5, .9))

            widget = QtGui.QWidget()
            layout = QtGui.QHBoxLayout()
            widget.setLayout(layout)
            
            label = QtGui.QLabel('A nice looking popup')
            layout.addWidget(label)
            
            btn = QtGui.QPushButton('Push Me')
            layout.addWidget(btn)

            popup.setCentralWidget(widget)
            popup.show()
            self.p = popup

        def showTooltip(self, checked=False):
            sender = self.sender()
            tooltip = QPopupTooltip(sender)
            tooltip.setAnchor('right')
            tooltip.setArrowSize(10)
            tooltip.setRelativePos((.9, 0.5))
            tooltip.setCentralWidget(QtGui.QLabel('A cool tooltip!!!'))
            tooltip.show()
            #self.t = tooltip

    app = QtGui.QApplication(sys.argv)

    qb = Test()
    qb.show()
    sys.exit(app.exec_())
