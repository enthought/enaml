#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

from .qt.QtGui import QWidget, QWidgetItem
from .qt.QtCore import Qt
from .qt_messenger_widget import QtMessengerWidget


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
        get = attrs.get
        self.set_min_size(get('min_size', (-1, -1)))
        self.set_max_size(get('max_size', (-1, -1)))
        self.set_bgcolor(get('bgcolor', ''))
        self.set_fgcolor(get('fgcolor', ''))
        self.set_font(get('font', ''))
        self.set_enabled(get('enabled', True))
        self.set_visible(get('visible', True))
        self.set_show_focus_rect(get('show_focus_rect', None))

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
    def on_message_set_enabled(self, payload):
        """ Process the 'set-enabled' message from Enaml.

        """
        self.set_enabled(payload['enabled'])

    def on_message_set_visible(self, payload):
        """ Process the 'set-visible' message from Enaml.
        
        """
        self.set_visible(payload['visble'])

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

    def on_message_set_min_size(self, payload):
        """ Process the 'set-min_size' message from Enaml.

        """
        self.set_min_size(payload['min_size'])

    def on_message_set_max_size(self, payload):
        """ Process the 'set-max_size' message from Enaml.

        """
        self.set_max_size(payload['max_size'])

    def on_message_set_show_focus_rect(self, payload):
        """ Process the 'set-show_focus_rect' message from Enaml.

        """
        self.set_show_focus_rect(payload['show_focus_rect'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_min_size(self, min_size):
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
        self.widget.setMinimumSize(*min_size)

    def set_max_size(self, max_size):
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
        self.widget.setMaximumSize(*max_size)

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

