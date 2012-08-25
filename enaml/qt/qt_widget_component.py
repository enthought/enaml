#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

from enaml.common.colors import parse_color

from .qt.QtGui import QWidget, QWidgetItem, QColor, QApplication
from .qt.QtCore import Qt, QSize
from .qt_messenger_widget import QtMessengerWidget


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
        qcolor = QColor(r, g, b, a * 255)
    return qcolor


class QtWidgetComponent(QtMessengerWidget):
    """ A Qt4 implementation of an Enaml WidgetComponent.

    """
    #: An attribute which will hold the default focus rect state if
    #: it is ever changed by the user.
    _default_focus_attr = None

    #: An attribute which will hold the widget item for the widget.
    _widget_item = None

    def create_widget(self, parent, tree):
        """ Creates the underlying QWidget object.

        """
        return QWidget(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtWidgetComponent, self).create(tree)
        self.set_minimum_size(tree['minimum_size'])
        self.set_maximum_size(tree['maximum_size'])
        self.set_bgcolor(tree['bgcolor'])
        self.set_fgcolor(tree['fgcolor'])
        self.set_font(tree['font'])
        self.set_enabled(tree['enabled'])
        self.set_visible(tree['visible'])
        self.set_show_focus_rect(tree['show_focus_rect'])

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
        widget = self.widget()
        role = widget.backgroundRole()
        qcolor = q_parse_color(bgcolor)
        if not qcolor.isValid():
            palette = QApplication.instance().palette(widget)
            qcolor = palette.color(role)
            # On OSX, the default color is rendered *slightly* off
            # so a simple workaround is to tell the widget not to
            # auto fill the background.
            widget.setAutoFillBackground(False)
        else:
            # When not using qt style sheets to set the background
            # color, we need to tell the widget to auto fill the 
            # background or the bgcolor won't render at all.
            widget.setAutoFillBackground(True)
        palette = widget.palette()
        palette.setColor(role, qcolor)
        widget.setPalette(palette)

    def set_fgcolor(self, fgcolor):
        """ Set the foreground color on the underlying widget.

        Parameters
        ----------
        fgcolor : str
            The foreground color of the widget as a CSS color string.

        """
        widget = self.widget()
        role = widget.foregroundRole()
        qcolor = q_parse_color(fgcolor)
        if not qcolor.isValid():
            palette = QApplication.instance().palette(widget)
            qcolor = palette.color(role)
        palette = widget.palette()
        palette.setColor(role, qcolor)
        widget.setPalette(palette)

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

