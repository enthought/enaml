#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------

""" A tooltip implementation using new-style popups

"""

import QtCore, QtGui
from q_popup_widget import QPopupWidget


class QPopupTooltip(QPopupWidget):

    def __init__(self, parent):
        super(QPopupTooltip, self).__init__(parent)

        self.setAnchor('right')
        self.setRelativePos((1., 0.5))
        self.setRadius(10)
        self.setArrowSize(10)

        self._expireTimer = QtCore.QBasicTimer()
        self._hideTimer = QtCore.QBasicTimer()

        self.setMouseTracking(True)

        self._rect = parent.rect()
        self.restartExpireTimer()

    def restartExpireTimer(self):
        # restart expiry timer
        self._hideTimer.stop()
        time = 10000
        self._expireTimer.start(time, self)

    def mouseMoveEvent(self, event):
        pos = self.parent().mapFromGlobal(event.globalPos())
        if not self._rect.contains(pos):
            self.hideTip()
        super(QPopupTooltip, self).mouseMoveEvent(event)

    def showEvent(self, event):
        QtGui.QApplication.instance().installEventFilter(self)
        super(QPopupTooltip, self).showEvent(event)
    
    def hideEvent(self, event):
        QtGui.QApplication.instance().removeEventFilter(self)
        super(QPopupTooltip, self).hideEvent(event)

    def hideTip(self):
        if not self._hideTimer.isActive():
            self._hideTimer.start(200, self)

    def hideTipImmediately(self):
        self.close()
        self.deleteLater()

    def timerEvent(self, event):
        timerId = event.timerId()
        if (timerId == self._hideTimer.timerId() or
            timerId == self._expireTimer.timerId()):
            # Stop both timers
            self._hideTimer.stop()
            self._expireTimer.stop()

            if (QtGui.QApplication.isEffectEnabled(QtCore.Qt.UI_FadeTooltip)):
                # fade tooltip
                self.hide()
            else:
                self.hideTipImmediately()

    def eventFilter(self, object, event):
        t = event.type()
        Qt = QtCore.Qt
        QE = QtCore.QEvent
        if (t == QE.KeyPress or t == QE.KeyRelease):
            key = event.key()
            mody = event.modifiers()
            if (not (mody & Qt.KeyboardModifierMask) and key != Qt.Key_Shift
                and key != Qt.Key_Control and key != Qt.Key_Alt and key != Qt.Key_Meta):
                self.hideTip()
        #elif t == QE.Leave and object == self.parent():
        #    print object, t
        #    self.hideTip()
        elif t in set([QE.WindowActivate, QE.WindowDeactivate, QE.MouseButtonPress,
                       QE.MouseButtonRelease, QE.MouseButtonDblClick, QE.FocusIn,
                       QE.FocusOut, QE.Wheel]):
            self.hideTipImmediately()
        elif (t == QE.MouseMove and object == self.parent()):
            if not self._rect.isNull() and not self._rect.contains(event.pos()):
              self.hideTip()
        return False
