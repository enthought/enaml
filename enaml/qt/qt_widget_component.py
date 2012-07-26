#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

from .qt.QtGui import QWidget, QWidgetItem, QDrag, QPixmap
from .qt.QtCore import Qt, QSize, QMimeData, QByteArray
from .qt_messenger_widget import QtMessengerWidget
from ..utils import WeakMethod


class QtWidgetComponent(QtMessengerWidget):
    """ A Qt4 implementation of an Enaml WidgetComponent.

    """
    #: An attribute which will hold the defautl focus rect state if
    #: it is ever changed by the user.
    _default_focus_attr = None

    def create(self):
        """ Creates the underlying QWidget object.

        """
        self.widget = QWidget(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the attributes of the underlying QWidget.

        """
        super(QtWidgetComponent, self).initialize(attrs)
        self.set_accepts_drops(attrs['accept_drops'])
        self.set_draggable(attrs['draggable'])
        self.set_drag_type(attrs['drag_type'])
        self.set_drop_types(attrs['drop_types'])
        self.set_minimum_size(attrs['minimum_size'])
        self.set_maximum_size(attrs['maximum_size'])
        self.set_bgcolor(attrs['bgcolor'])
        self.set_fgcolor(attrs['fgcolor'])
        self.set_font(attrs['font'])
        self.set_enabled(attrs['enabled'])
        self.set_visible(attrs['visible'])
        self.set_show_focus_rect(attrs['show_focus_rect'])

        self.widget.mousePressEvent = WeakMethod(self.mousePressEvent)
        self.widget.dragEnterEvent = WeakMethod(self.dragEnterEvent)
        self.widget.dragLeaveEvent = WeakMethod(self.dragLeaveEvent)
        self.widget.dropEvent = WeakMethod(self.dropEvent)

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------
    @property
    def widget_item(self):
        """ A readonly cached property which returns the QWidgetItem
        for the underlying Qt widget.

        """
        try:
            res = self.__widget_item
        except AttributeError:
            res = self.__widget_item = QWidgetItem(self.widget)
        return res

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_accept_drops(self, payload):
        """ Process the 'set-accept_drops' message from Enaml.

        """
        self.set_accepts_drops(payload['accept_drops'])

    def on_message_set_draggable(self, payload):
        """ Process the 'set-draggable' message from Enaml.

        """
        self.set_draggable(payload['draggable'])

    def on_message_set_drag_type(self, payload):
        """ Process the 'set-drag_type' message from Enaml.

        """
        self.set_drag_type(payload['drag_type'])

    def on_message_set_drop_types(self, payload):
        """ Process the 'set-drop_types' message from Enaml.

        """
        self.set_drop_types(payload['drop_types'])

    def on_message_set_enabled(self, payload):
        """ Process the 'set-enabled' message from Enaml.

        """
        self.set_enabled(payload['enabled'])

    def on_message_set_visible(self, payload):
        """ Process the 'set-visible' message from Enaml.

        """
        self.set_visible(payload['visible'])

    def on_message_set_bgcolor(self, payload):
        """ Process the 'set-bgcolor' message from Enaml.

        """
        self.set_bgcolor(payload['bgcolor'])

    def on_message_set_fgcolor(self, payload):
        """ Process the 'set-fgcolor' message from Enaml.

        """
        self.set_fgcolor(payload['fgcolor'])

    def on_message_set_font(self, payload):
        """ Process the 'set-font' message from Enaml.

        """
        self.set_font(payload['font'])

    def on_message_set_minimum_size(self, payload):
        """ Process the 'set-minimum_size' message from Enaml.

        """
        self.set_minimum_size(payload['minimum_size'])

    def on_message_set_maximum_size(self, payload):
        """ Process the 'set-maximum_size' message from Enaml.

        """
        self.set_maximum_size(payload['maximum_size'])

    def on_message_set_show_focus_rect(self, payload):
        """ Process the 'set-show_focus_rect' message from Enaml.

        """
        self.set_show_focus_rect(payload['show_focus_rect'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_accepts_drops(self, accept_drops):
        """ Set whether or not the widget accepts drops

        """
        self.widget.setAcceptDrops(accept_drops)

    def set_draggable(self, draggable):
        """ Set whether or not the widget is draggable.

        """
        self.draggable = draggable

    def set_drag_type(self, drag_type):
        """ Set the mime-type being dragged

        """
        self.drag_type = drag_type

    def set_drop_types(self, drop_types):
        """ Set the mime-types that are allowed to be dropped on the widget.

        """
        self.drop_types = drop_types

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
        self.widget.setMinimumSize(QSize(*min_size))

    def set_maximum_size(self, max_size):
        """ Sets the maximum size on the underlying widget.

        Parameters
        ----------
        max_size : (int, int)
            The minimum size allowable for the widget. A value of
            (-1, -1) indicates the default min size.

        """
        # QWidget uses 16777215 as the max size
        if -1 in max_size:
            max_size = (16777215, 16777215)
        self.widget.setMaximumSize(QSize(*max_size))

    def set_enabled(self, enabled):
        """ Set the enabled state on the underlying widget.

        Parameters
        ----------
        enabled : bool
            Whether or not the widget is enabled.

        """
        self.widget.setEnabled(enabled)

    def set_visible(self, visible):
        """ Set the visibility state on the underlying widget.

        Parameters
        ----------
        visible : bool
            Whether or not the widget is visible.

        """
        self.widget.setVisible(visible)

    def set_bgcolor(self, bgcolor):
        """ Set the background color on the underlying widget.

        Parameters
        ----------
        bgcolor : str
            The background color of the widget as a CSS color string.

        """
        pass

    def set_fgcolor(self, fgcolor):
        """ Set the foreground color on the underlying widget.

        Parameters
        ----------
        fgcolor : str
            The foreground color of the widget as a CSS color string.

        """
        pass

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
            attr = Qt.WA_MacShowFocusRect
            if show is None:
                if self._default_focus_attr is not None:
                    self.widget.setAttribute(attr, self._default_focus_attr)
            else:
                if self._default_focus_attr is None:
                    self._default_focus_attr = self.widget.testAttribute(attr)
                self.widget.setAttribute(attr, show)

    #--------------------------------------------------------------------------
    # Drag and drop
    #--------------------------------------------------------------------------
    def drag_repr(self):
        """ An image representation of the widget. This method can be overridden
        for custom representations.

        """
        return QPixmap.grabWidget(self.widget)

    def drag_data(self):
        """ The data to be dragged. This method should be overriden by any
        subclasses.

        """
        raise NotImplementedError("The 'drag_data' method must be implemented.")

    def hover_enter(self):
        """ Fired when the dragged object enters the widget. This method can be
        overriden for custom styling.

        """
        self.widget.setStyleSheet("QWidget{background-color:rgba(0,0,255,25);}")

    def hover_exit(self):
        """ Fired when the dragged object leaves the widget. This method can be
        overriden for custom styling.

        """
        self.widget.setStyleSheet("QWidget { background-color: rgba(0,0,0,0);}")

    def mousePressEvent(self, event):
        """ Mouse clicked handler

        """
        if self.draggable:
            if event.button() == Qt.LeftButton:
                drag = QDrag(self.widget)
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
        self.hover_exit()
        payload = {
            'action': 'dropped',
            'data': str(event.mimeData().data(self.selected_type))
        }
        self.send_message(payload)
        event.acceptProposedAction()
