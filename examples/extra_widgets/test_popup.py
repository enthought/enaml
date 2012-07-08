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

if __name__ == "__main__":

    class Test(QtGui.QWidget):
        def __init__(self, parent=None):
            super(Test, self).__init__(parent)
            self.setWindowTitle('Test popup')
            
            layout = QtGui.QHBoxLayout()
            self.setLayout(layout)
            self.b1 = QtGui.QPushButton('Popup')
            self.b1.clicked.connect(self.showPopup)
            layout.addWidget(self.b1)

        def showPopup(self, checked=False):
            sender = self.sender()
            popup = QPopupWidget(sender)
            popup.setAnchor('right')
            popup.setArrowSize(10)
            popup.setRelativePos((1.0, 0.5))
            popup.setCentralWidget(QtGui.QLabel('A nice looking popup'))
            popup.show()
            self.p = popup

    app = QtGui.QApplication(sys.argv)

    qb = Test()
    qb.show()
    sys.exit(app.exec_())
