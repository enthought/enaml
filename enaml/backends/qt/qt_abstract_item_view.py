#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import QSize
from .qt.QtGui import QAbstractItemView
from .qt_control import QtControl
from .abstract_item_model_wrapper import AbstractItemModelWrapper

from ...components.abstract_item_view import AbstractTkItemView


SCROLL_MODE_MAP = {
    'pixel': QAbstractItemView.ScrollPerPixel,
    'item': QAbstractItemView.ScrollPerItem,
}


class QtAbstractItemView(QtControl, AbstractTkItemView):
    """ An abstract base class for implementing Qt item views.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying QItemView control.

        """
        raise NotImplementedError

    def initialize(self):
        """ Initialize the widget with the attributes of this instance.

        """
        super(QtAbstractItemView, self).initialize()
        shell = self.shell_obj
        self.set_item_model(shell.item_model)
        self.set_icon_size(shell.icon_size)
        self.set_horizontal_scroll_mode(shell.horizontal_scroll_mode)
        self.set_vertical_scroll_mode(shell.vertical_scroll_mode)

    def bind(self):
        """ Bind any event/signal handlers for the Qt Widget.

        """
        super(QtAbstractItemView, self).bind()
        widget = self.toolkit_widget
        widget.activated.connect(lambda idx: self._send_event(idx, 'activated'))
        widget.clicked.connect(lambda idx: self._send_event(idx, 'clicked'))
        widget.doubleClicked.connect(lambda idx: self._send_event(idx, 'double_clicked'))

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_item_model_changed(self, item_model):
        """ The change handler for the 'item_model' attribute on the 
        shell object.

        """
        self.set_item_model(item_model)

    def shell_icon_size_changed(self, size):
        """ The change handle for the 'icon_size' attribute on the 
        shell object.

        """
        self.set_icon_size(size)

    def shell_horizontal_scroll_mode_changed(self, mode):
        """ The change handler for the 'horizontal_scroll_mode' attribute
        on the shell object.

        """
        self.set_horizontal_scroll_mode(mode)

    def shell_vertical_scroll_mode_changed(self, mode):
        """ The change handler for the 'vertical_scroll_mode' attribute
        on the shell object.

        """
        self.set_vertical_scroll_mode(mode)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_item_model(self, item_model):
        """ Sets the model to use for the view.

        """
        # Save the model wrapper. PySide's object cache is sometimes unreliable
        # in various versions.
        self.model_wrapper = AbstractItemModelWrapper(item_model)
        self.widget.setModel(self.model_wrapper)

    def set_icon_size(self, size):
        """ Sets the icon size on the underlying widget.

        """
        self.widget.setIconSize(QSize(*size))

    def set_horizontal_scroll_mode(self, mode):
        """ Sets the horizontal scrolling mode of the widget.

        """
        qmode = SCROLL_MODE_MAP[mode]
        self.widget.setHorizontalScrollMode(qmode)

    def set_vertical_scroll_mode(self, mode):
        """ Sets the vertical scrolling mode of the widget.

        """
        qmode = SCROLL_MODE_MAP[mode]
        self.widget.setVerticalScrollMode(qmode)

    def set_bgcolor(self, bgcolor):
        """ Overridden parent class method to properly manipulate the
        background of the underlying viewport so that colors are set
        properly.

        """
        if bgcolor:
            self.widget.viewport().setAutoFillBackground(False)
        else:
            self.widget.viewport().setAutoFillBackground(True)
        return super(QtAbstractItemView, self).set_bgcolor(bgcolor)

    #--------------------------------------------------------------------------
    # Event notification methods
    #--------------------------------------------------------------------------
    def _send_event(self, qindex, trait):
        """ Send a ModelIndex to the given shell trait.

        """
        model = self.model_wrapper
        index = model.from_q_index(qindex)
        getattr(self.shell_obj, trait)(index)

