#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

from enaml.colors import parse_color

from .qt.QtGui import QWidget, QWidgetItem, QColor, QApplication, QPixmap, QDrag
from .qt.QtCore import Qt, QSize, QMimeData, QByteArray
from .qt_object import QtObject


def q_parse_color(color):
    """ Convert a color string into a QColor.

    Parameters
    ----------
    color : string
        A CSS3 color string to convert to a QColor.

    Returns
    -------
    result : QColor
        The QColor for the given color string

    """
    rgba = parse_color(color)
    if rgba is None:
        qcolor = QColor()
    else:
        r, g, b, a = rgba
        qcolor = QColor.fromRgbF(r, g, b, a)
    return qcolor


class QtWidget(QtObject):
    """ A Qt4 implementation of an Enaml Widget.

    """
    #: An attribute which will hold the default focus rect state if
    #: it is ever changed by the user.
    _default_focus_attr = None

    #: An attribute which will hold the widget item for the widget.
    _widget_item = None

    #: An attribute which indicates whether or not the background
    #: color of the widget has been changed.
    _bgcolor_changed = False

    #: An attribute which indicates whether or not the foreground
    #: color of the widget has been changed.
    _fgcolor_changed = False

    def create_widget(self, parent, tree):
        """ Creates the underlying QWidget object.

        """
        return QWidget(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtWidget, self).create(tree)
        self.set_minimum_size(tree['minimum_size'])
        self.set_maximum_size(tree['maximum_size'])
        self.set_bgcolor(tree['bgcolor'])
        self.set_fgcolor(tree['fgcolor'])
        self.set_font(tree['font'])
        self.set_enabled(tree['enabled'])
        self.set_visible(tree['visible'])
        self.set_show_focus_rect(tree['show_focus_rect'])
        self.set_tool_tip(tree['tool_tip'])
        self.set_status_tip(tree['status_tip'])
        self.set_accept_drops(tree['accept_drops'])
        self.set_accept_drags(tree['accept_drags'])
        self.set_drag_type(tree['drag_type'])
        self.set_drop_types(tree['drop_types'])

        self.widget().mousePressEvent = self.mousePressEvent
        self.widget().dragEnterEvent = self.dragEnterEvent
        self.widget().dragLeaveEvent = self.dragLeaveEvent
        self.widget().dropEvent = self.dropEvent

    #--------------------------------------------------------------------------
    # Public Api
    #--------------------------------------------------------------------------
    def widget_item(self):
        """ Get the QWidgetItem for the underlying widget.

        Returns
        -------
        result : QWidgetItem
            The QWidgetItem to use for the underlying widget.

        """
        res = self._widget_item
        if res is None:
            res = self._widget_item = QWidgetItem(self.widget())
        return res

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_enabled(self, content):
        """ Handle the 'set_enabled' action from the Enaml widget.

        """
        self.set_enabled(content['enabled'])

    def on_action_set_visible(self, content):
        """ Handle the 'set_visible' action from the Enaml widget.

        """
        self.set_visible(content['visible'])

    def on_action_set_bgcolor(self, content):
        """ Handle the 'set_bgcolor' action from the Enaml widget.

        """
        self.set_bgcolor(content['bgcolor'])

    def on_action_set_fgcolor(self, content):
        """ Handle the 'set_fgcolor' action from the Enaml widget.

        """
        self.set_fgcolor(content['fgcolor'])

    def on_action_set_font(self, content):
        """ Handle the 'set_font' action from the Enaml widget.

        """
        self.set_font(content['font'])

    def on_action_set_minimum_size(self, content):
        """ Handle the 'set_minimum_size' action from the Enaml widget.

        """
        self.set_minimum_size(content['minimum_size'])

    def on_action_set_maximum_size(self, content):
        """ Handle the 'set_maximum_size' action from the Enaml widget.

        """
        self.set_maximum_size(content['maximum_size'])

    def on_action_set_show_focus_rect(self, content):
        """ Handle the 'set_show_focus_rect' action from the Enaml
        widget.

        """
        self.set_show_focus_rect(content['show_focus_rect'])

    def on_action_set_tool_tip(self, content):
        """ Handle the 'set_tool_tip' action from the Enaml widget.

        """
        self.set_tool_tip(content['tool_tip'])

    def on_action_set_status_tip(self, content):
        """ Handle the 'set_status_tip' action from the Enaml widget.

        """
        self.set_status_tip(content['status_tip'])

    def on_action_set_accept_drops(self, content):
        """ Handle the 'set_accept_drops' action from the Enaml widget.

        """
        self.set_accept_drops(content['accept_drops'])

    def on_action_set_accept_drags(self, content):
        """ Handle the 'set_accept_drags' action from the Enaml widget.

        """
        self.set_accept_drags(content['accept_drags'])

    def on_action_set_drag_type(self, content):
        """ Handle the 'set_drag_type' action from the Enaml widget.

        """
        self.set_drag_type(content['drag_type'])

    def on_action_set_drop_types(self, content):
        """ Handle the 'set_drop_types' action from the Enaml widget.

        """
        self.set_drop_types(content['drop_types'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_minimum_size(self, min_size):
        """ Sets the minimum size on the underlying widget.

        Parameters
        ----------
        min_size : (int, int)
            The minimum size allowable for the widget. A value of
            (-1, -1) indicates the default min size.

        """
        # QWidget uses (0, 0) as the minimum size.
        if -1 in min_size:
            min_size = (0, 0)
        self.widget().setMinimumSize(QSize(*min_size))

    def set_maximum_size(self, max_size):
        """ Sets the maximum size on the underlying widget.

        Parameters
        ----------
        max_size : (int, int)
            The minimum size allowable for the widget. A value of
            (-1, -1) indicates the default max size.

        """
        # QWidget uses 16777215 as the max size
        if -1 in max_size:
            max_size = (16777215, 16777215)
        self.widget().setMaximumSize(QSize(*max_size))

    def set_enabled(self, enabled):
        """ Set the enabled state on the underlying widget.

        Parameters
        ----------
        enabled : bool
            Whether or not the widget is enabled.

        """
        self.widget().setEnabled(enabled)

    def set_visible(self, visible):
        """ Set the visibility state on the underlying widget.

        Parameters
        ----------
        visible : bool
            Whether or not the widget is visible.

        """
        self.widget().setVisible(visible)

    def set_bgcolor(self, bgcolor):
        """ Set the background color on the underlying widget.

        Parameters
        ----------
        bgcolor : str
            The background color of the widget as a CSS color string.

        """
        if bgcolor or self._bgcolor_changed:
            widget = self.widget()
            role = widget.backgroundRole()
            qcolor = q_parse_color(bgcolor)
            if not qcolor.isValid():
                app_palette = QApplication.instance().palette(widget)
                qcolor = app_palette.color(role)
                widget.setAutoFillBackground(False)
            else:
                widget.setAutoFillBackground(True)
            palette = widget.palette()
            palette.setColor(role, qcolor)
            widget.setPalette(palette)
            self._bgcolor_changed = True

    def set_fgcolor(self, fgcolor):
        """ Set the foreground color on the underlying widget.

        Parameters
        ----------
        fgcolor : str
            The foreground color of the widget as a CSS color string.

        """
        if fgcolor or self._fgcolor_changed:
            widget = self.widget()
            role = widget.foregroundRole()
            qcolor = q_parse_color(fgcolor)
            if not qcolor.isValid():
                app_palette = QApplication.instance().palette(widget)
                qcolor = app_palette.color(role)
            palette = widget.palette()
            palette.setColor(role, qcolor)
            widget.setPalette(palette)
            self._fgcolor_changed = True

    def set_font(self, font):
        """ Set the font on the underlying widget.

        Parameters
        ----------
        font : str
            The font for the widget as a CSS font string.

        """
        pass

    def set_show_focus_rect(self, show):
        """ Sets whether or not to show the focus rectangle around
        the widget. This is currently only supported on OSX.

        """
        if sys.platform == 'darwin':
            widget = self.widget()
            attr = Qt.WA_MacShowFocusRect
            if show is None:
                if self._default_focus_attr is not None:
                    widget.setAttribute(attr, self._default_focus_attr)
            else:
                if self._default_focus_attr is None:
                    self._default_focus_attr = widget.testAttribute(attr)
                widget.setAttribute(attr, show)

    def set_tool_tip(self, tool_tip):
        """ Set the tool tip for this widget.

        """
        self.widget().setToolTip(tool_tip)

    def set_status_tip(self, status_tip):
        """ Set the status tip for this widget.

        """
        self.widget().setStatusTip(status_tip)

    def set_accept_drops(self, accept_drops):
        """ Set whether or not the widget accepts drops

        """
        self.widget().setAcceptDrops(accept_drops)

    def set_accept_drags(self, accept_drags):
        """ Set whether or not the widget is draggable.

        """
        self.accept_drags = accept_drags

    def set_drag_type(self, drag_type):
        """ Set the mime-type being dragged

        """
        self.drag_type = drag_type

    def set_drop_types(self, drop_types):
        """ Set the mime-types that are allowed to be dropped on the widget.

        """
        self.drop_types = drop_types

    #--------------------------------------------------------------------------
    # Drag and drop
    #--------------------------------------------------------------------------
    def drag_repr(self):
        """ An image representation of the widget. This method can be overridden
        for custom representations.

        """
        return QPixmap.grabWidget(self.widget())

    def drag_data(self):
        """ The data to be dragged. This method should be overriden by any
        subclasses.

        """
        raise NotImplementedError("The 'drag_data' method must be implemented.")

    def hover_enter(self):
        """ Fired when the dragged object enters the widget. This method can be
        overriden for custom styling.

        """
        self.widget().setStyleSheet("QWidget{background-color:rgba(0,0,255,25);}")

    def hover_exit(self):
        """ Fired when the dragged object leaves the widget. This method can be
        overriden for custom styling.

        """
        self.widget().setStyleSheet("QWidget{background-color:rgba(0,0,0,0);}")

    def mousePressEvent(self, event):
        """ Mouse clicked handler

        """
        if self.accept_drags:
            if event.button() == Qt.LeftButton:
                drag = QDrag(self.widget())
                mime_data = QMimeData()
                mime_data.setData(self.drag_type, QByteArray(self.drag_data()))
                drag.setMimeData(mime_data)
                drag.setPixmap(self.drag_repr())
                drag.exec_(Qt.CopyAction)

    def dragEnterEvent(self, event):
        """ Fired when a dragged object is hovering over the widget

        """
        self.hover_enter()
        for format in event.mimeData().formats():
            if format in self.drop_types:
                self.selected_type = format
                event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        """ Fire when an object is dragged off the widget

        """
        self.hover_exit()

    def dropEvent(self, event):
        """ Fired when an object is dropped on the widget

        """
        content = {'data': event.mimeData().data(self.selected_type)}
        self.send_action('dropped', content)
        event.acceptProposedAction()
        self.hover_exit()
