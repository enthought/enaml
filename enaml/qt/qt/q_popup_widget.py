#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------

""" An implementation of a popup widget with rounded corners and an arrow 
anchoring it to an underlying widget. Useful for transient dialogs.
"""

import sys
import QtGui, QtCore

# Implementation of Popup widget

class QPopupWidget(QtGui.QWidget):
    
    def __init__(self, parent):
        super(QPopupWidget, self).__init__(parent)

        # Set up the window flags to get a non-bordered window
        if sys.platform == "win32":
            self.setWindowFlags(QtCore.Qt.ToolTip |
                                QtCore.Qt.FramelessWindowHint)
        else:
            self.setWindowFlags(QtCore.Qt.Popup |
                                QtCore.Qt.WindowStaysOnTopHint)

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self._fade_time = 50

        layout = QtGui.QGridLayout()
        layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        layout.setContentsMargins(10,10,10,10)
        self.setLayout(layout)

        # Default anchoring and configuration options
        self.setAnchor('bottom')
        self.setRelativePos((0.5, 0.5))
        self.setArrowSize(20)
        self.setRadius(10)

    def setCentralWidget(self, widget):
        """ Set the central widget in the popup

        Parameters
        ---------
        widget : QWidget
            The widget to show in the popup.

        """
        layout = self.layout()
        layout.addWidget(widget)

    def setAnchor(self, anchor):
        """ Set the positioning of the popup relative to the parent widget.

        Parameters
        ----------
        anchor : String
            Can be one of 'left', 'right', 'top', 'bottom'

        """
        if anchor not in set(['left', 'right', 'top', 'bottom']):
            raise Exception("anchor must be one of 'left', 'right', 'top', 'bottom'")
        self._anchor_type = anchor
        if self.isVisible(): self._rebuild()

    def anchor(self):
        """ Return the relative positioning

        Returns
        -------
        result : String
            A string specifying the position relative to the parent widget

        """
        return self._anchor_type

    def setArrowSize(self, arrow):
        """ Set size of the arrow.

        Parameters
        ----------
        arrow : Int
            The size of the arrow (in pixels). A size of zero indicates
            that no arrow is desired

        """
        if arrow < 0:
            raise Exception("Arrow size must be greater than or equal to 0")
        self._arrow = QtCore.QSize(arrow/1.5, arrow)
        if self.isVisible(): self._rebuild()

    def arrowSize(self):
        """ Return the size of the arrow.

        Returns
        -------
        result : Int
            The size of the arrow (in pixels)

        """
        return self._arrow.height()

    def setRadius(self, radius):
        """ Set the radius of the popup corners

        Parameters
        ----------
        radius : Int
            The radius of the popup corners (in pixels). Must be greater than 0.

        """
        if radius <= 0:
            raise Exception("Radius must be greater than 0")
        self._radius = radius
        if self.isVisible(): self._rebuild()

    def radius(self):
        """ Return the radius of the corners

        Returns
        -------
        result : Int
            The radius of the popup corners (in pixels)

        """
        return self._radius

    def setRelativePos(self, pos):
        """ Set the position of the anchor point (the tip of the arrow)
        relative the bounds of the parent widget.i

        Parameters
        ----------
        pos : A ([0,1], [0,1]) tuple specifying the position in relative coords

        """
        self._relative_pos = pos
        if self.isVisible(): self._rebuild()

    def relativePos(self):
        """ Return the relative position of the popup

        Returns
        -------
        result : Tuple
            The relative anchoring of the popup relative to the parent's bounds

        """
        return self._relative_pos

    def show(self):
        """ Fade the popup in

        """
        self.__a = a = QtCore.QPropertyAnimation(self, "windowOpacity", self)
        a.setDuration(self._fade_time)
        a.setStartValue(0)
        a.setEndValue(1)
        a.start()
        super(QPopupWidget, self).show()

    def hide(self):
        """ Fade the popup out

        """
        self.__a = a = QtCore.QPropertyAnimation(self, "windowOpacity", self)
        a.setDuration(self._fade_time)
        a.setStartValue(1)
        a.setEndValue(0)
        a.start()
        QtCore.QTimer.singleShot(self._fade_time, super(QPopupWidget,self).hide)

    def setMinimumSize(self, width, height):
        """ Override the minimum size to account for the extra
        space used by the arrow

        """
        m =  self.contentsMargins()
        width += m.right() + m.left()
        height += m.top() + m.bottom()
        super(QPopupWidget, self).setMinimumSize(width, height)

    def paintEvent(self, event):
        """ Draw the popup, rendering the rounded path using the palette's
        window color.

        """
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        palette = self.palette()
        painter.setPen(palette.dark().color())
        painter.setBrush(palette.window())
        painter.drawPath(self._path)

    def resizeEvent(self, event):
        self._rebuild()
        super(QPopupWidget, self).resizeEvent(event)

    def _rebuild(self):
        """ Rebuild the path used to draw the outline of the popup

        """
        # anchor to center of parent
        anchor = self.parent()
        anchor_size = anchor.size()
        pt = QtCore.QPoint(anchor_size.width()*self._relative_pos[0],
                           anchor_size.height()*self._relative_pos[1])
        anchor_pt = anchor.mapToGlobal(pt)

        h = self._arrow.height()
        size = self.size()
        margins = QtCore.QMargins()
        anchor_type = self._anchor_type
        if anchor_type == 'right':
            adj = QtCore.QPoint(0, size.height()/2)
            margins.setLeft(h)
        elif anchor_type == 'bottom':
            adj = QtCore.QPoint(size.width()/2, 0)
            margins.setTop(h)
        elif anchor_type == 'left':
            adj = QtCore.QPoint(size.width(), size.height()/2)
            margins.setRight(h)
        else:
            adj = QtCore.QPoint(size.width()/2, size.height())
            margins.setBottom(h)
        self.move(anchor_pt - adj)
        self.setContentsMargins(margins)
        
        self._path = _generate_popup_path(self.rect(),
                                        self._radius, self._radius,
                                        self._arrow, anchor_type)


def _generate_popup_path(rect, xRadius, yRadius, arrowSize, anchor):
    """ Generate the QPainterPath used to draw the outline of the popup

    Parameters
    ----------
    rect : QRect
        Bounding QRect for the popup
    xRadius, yRadius : Int
        Radii of the 
    arrowSize : QSize
        Width and height of the popup anchor arrow
    anchor : Int
        Positioning of the popup relative to the parent. Determines the position
        of the arrow

    Returns
    -------
    result : QPainterPath
        Path that can be passed to QPainter.drawPath to render popup

    """

    awidth, aheight = arrowSize.width(), arrowSize.height()
    draw_arrow = (awidth > 0 and aheight > 0)

    if anchor == 'right':
        rect.adjust(aheight,0, 0, 0)
    elif anchor == 'left':
        rect.adjust(0,0,-aheight, 0)
    elif anchor == 'bottom':
        rect.adjust(0,aheight,0, 0)
    else:
        rect.adjust(0,0,0,-aheight)

    r = rect.normalized()

    if r.isNull():
        return

    hw = r.width() / 2
    hh = r.height() / 2

    xRadius = 100 * min(xRadius, hw) / hw
    yRadius = 100 * min(yRadius, hh) / hh

    # The starting point of the path is the top left corner
    x = r.x()
    y = r.y()
    w = r.width()
    h = r.height()
    rxx2 = w*xRadius/100
    ryy2 = h*yRadius/100

    center = r.center()

    path = QtGui.QPainterPath()
    path.arcMoveTo(x, y, rxx2, ryy2, 180)
    path.arcTo(x, y, rxx2, ryy2, 180, -90)
    
    if anchor == 'bottom' and draw_arrow:
        path.lineTo(center.x() - awidth, y)
        path.lineTo(center.x(), y - aheight)
        path.lineTo(center.x() + awidth, y)
    
    path.arcTo(x+w-rxx2, y, rxx2, ryy2, 90, -90)
    
    if anchor == 'left' and draw_arrow:
        path.lineTo(x + w, center.y() - awidth)
        path.lineTo(x + w + aheight, center.y())
        path.lineTo(x + w, center.y() + awidth)
    
    path.arcTo(x+w-rxx2, y+h-ryy2, rxx2, ryy2, 0, -90)
    
    if anchor == 'top' and draw_arrow:
        path.lineTo(center.x() + awidth, y + h)
        path.lineTo(center.x(), y + h + aheight)
        path.lineTo(center.x() - awidth, y + h)
    
    path.arcTo(x, y+h-ryy2, rxx2, ryy2, 270, -90)
    
    if anchor == 'right' and draw_arrow:
        path.lineTo(x, center.y() + awidth)
        path.lineTo(x - aheight, center.y())
        path.lineTo(x,  center.y() - awidth)
    
    path.closeSubpath()
    return path
