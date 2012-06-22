#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QWidget
from .qt_messenger_widget import QtMessengerWidget


class QtWidgetComponent(QtMessengerWidget):
    """ A Qt4 implementation of the Enaml WidgetComponent class.

    """
    def create(self):
        """ Creates the underlying QWidget object.

        """
        self.widget = QWidget(self.parent_widget)

    def initialize(self, init_attrs):
        """ Initialize the attributes of the underlying QWidget.

        """
        get = init_attrs.get
        self.set_min_size(get('min_size', (-1, -1)))
        self.set_max_size(get('max_size', (-1, -1)))
        self.set_size_hint(get('size_hint', (-1, -1)))
        self.set_bgcolor(get('bgcolor', ''))
        self.set_fgcolor(get('fgcolor', ''))
        self.set_font(get('font', ''))
        self.set_enabled(get('enabled', True))
        self.set_visible(get('visible', True))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_enabled(self, ctxt):
        """ Process the 'set_enabled' message from Enaml.

        """
        return self.set_enabled(ctxt['value'])

    def receive_set_visible(self, ctxt):
        """ Process the 'set_visible' message from Enaml.
        
        """
        return self.set_visible(ctxt['value'])

    def receive_set_bgcolor(self, ctxt):
        """ Process the 'set_bgcolor' message from Enaml.

        """
        return self.set_bgcolor(ctxt['value'])

    def receive_set_fgcolor(self, ctxt):
        """ Process the 'set_fgcolor' message from Enaml.

        """
        return self.set_fgcolor(ctxt['value'])

    def receive_set_font(self, ctxt):
        """ Process the 'set_font' message from Enaml.

        """
        return self.set_font(ctxt['value'])

    def receive_set_size_hint(self, ctxt):
        """ Process the 'set_size_hint' message from Enaml.

        """
        return self.set_size_hint(ctxt['value'])

    def receive_set_min_size(self, ctxt):
        """ Process the 'set_min_size' message from Enaml.

        """
        return self.set_min_size(ctxt['value'])

    def receive_set_max_size(self, ctxt):
        """ Process the 'set_max_size' message from Enaml.

        """
        return self.set_max_size(ctxt['value'])
    
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
        return True

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
        return True

    def set_size_hint(self, size_hint):
        """ Sets the size hint on the underlying widget.

        Parameters
        ----------
        size_hint : (int, int)
            The size hint to use for the widget. A value of (-1, -1)
            indicates the default size hint.

        """
        # Setting the size hint is not currently supported.
        return False

    def set_enabled(self, enabled):
        """ Set the enabled state on the underlying widget.

        Parameters
        ----------
        enabled : bool
            Whether or not the widget is enabled.

        """
        self.widget.setEnabled(enabled)
        return True

    def set_visible(self, visible):
        """ Set the visibility state on the underlying widget.

        Parameters
        ----------
        visible : bool
            Whether or not the widget is visible.

        """
        self.widget.setVisible(visible)
        return True

    def set_bgcolor(self, bgcolor):
        """ Set the background color on the underlying widget.

        Parameters
        ----------
        bgcolor : str
            The background color of the widget as a CSS color string.

        """
        return False

    def set_fgcolor(self, fgcolor):
        """ Set the foreground color on the underlying widget.

        Parameters
        ----------
        fgcolor : str
            The foreground color of the widget as a CSS color string.

        """
        return False

    def set_font(self, font):
        """ Set the font on the underlying widget.

        Parameters
        ----------
        font : str
            The font for the widget as a CSS font string.

        """
        return False

