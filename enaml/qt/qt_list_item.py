#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from enaml.colors import parse_color

from .qt.QtCore import Qt, QSize
from .qt.QtGui import QListWidgetItem, QColor
from .qt_font_utils import QtFontCache
from .qt_object import QtObject


HORIZONTAL_ALIGN = {
    'left': Qt.AlignLeft,
    'right': Qt.AlignRight,
    'center': Qt.AlignHCenter,
    'justify': Qt.AlignJustify,
}


VERTICAL_ALIGN = {
    'top': Qt.AlignTop,
    'bottom': Qt.AlignBottom,
    'center': Qt.AlignVCenter,
}


class QtListItem(QtObject):
    """ A Qt implementation of an Enaml ListItem.

    """
    default_item = QListWidgetItem()

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying list widget item.

        """
        return QListWidgetItem(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtListItem, self).create(tree)
        self.set_text(tree['text'])
        self.set_tool_tip(tree['tool_tip'])
        self.set_status_tip(tree['status_tip'])
        self.set_background(tree['background'])
        self.set_foreground(tree['foreground'])
        self.set_font(tree['font'])
        self.set_icon_source(tree['icon_source'])
        self.set_checkable(tree['checkable'])
        self.set_selectable(tree['selectable'])
        self.set_checked(tree['checked'])
        self.set_selected(tree['selected'])
        self.set_enabled(tree['enabled'])
        self.set_visible(tree['visible'])
        self.set_text_align(tree['text_align'])
        self.set_vertical_text_align(tree['vertical_text_align'])
        self.set_preferred_size(tree['preferred_size'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        self.widget().setText(text)

    def set_tool_tip(self, tool_tip):
        self.widget().setToolTip(tool_tip)

    def set_status_tip(self, status_tip):
        self.widget().setStatusTip(status_tip)

    def set_background(self, background):
        qcolor = None
        if background:
            color = parse_color(background)
            if color is not None:
                qcolor = QColor.fromRgbF(*color)
        self.widget().setBackground(qcolor or self.default_item.background())

    def set_foreground(self, foreground):
        qcolor = None
        if foreground:
            color = parse_color(foreground)
            if color is not None:
                qcolor = QColor.fromRgbF(*color)
        self.widget().setForeground(qcolor or self.default_item.foreground())

    def set_font(self, font):
        widget = self.widget()
        if not font:
            if widget.data(Qt.FontRole) is not None:
                widget.setData(Qt.FontRole, None)
        else:
            parent = self.parent()
            cache = getattr(parent, '_items_font_cache', None)
            if cache is None:
                pfont = parent.widget().font()
                print 'creating font cache'
                cache = parent._items_font_cache = QtFontCache(pfont)
            widget.setData(Qt.FontRole, cache[font])

    def set_icon_source(self, icon_source):
        pass

    def set_checkable(self, checkable):
        widget = self.widget()
        flags = widget.flags()
        if checkable:
            flags |= Qt.ItemIsUserCheckable
        else:
            flags &= ~Qt.ItemIsUserCheckable
        widget.setFlags(flags)

    def set_selectable(self, selectable):
        widget = self.widget()
        flags = widget.flags()
        if selectable:
            flags |= Qt.ItemIsSelectable
        else:
            flags &= ~Qt.ItemIsSelectable
        widget.setFlags(flags)

    def set_checked(self, checked):
        widget = self.widget()
        if widget.flags() & Qt.ItemIsUserCheckable:
            state = Qt.Checked if checked else Qt.Unchecked
            self.widget().setCheckState(state)

    def set_selected(self, selected):
        self.widget().setSelected(selected)

    def set_enabled(self, enabled):
        widget = self.widget()
        flags = widget.flags()
        if enabled:
            flags |= Qt.ItemIsEnabled
        else:
            flags &= ~Qt.ItemIsEnabled
        widget.setFlags(flags)

    def set_visible(self, visible):
        self.widget().setHidden(not visible)

    def set_text_align(self, align):
        widget = self.widget()
        flags = widget.textAlignment()
        flags &= ~Qt.AlignHorizontal_Mask
        flags |= HORIZONTAL_ALIGN[align]
        widget.setTextAlignment(flags)

    def set_vertical_text_align(self, align):
        widget = self.widget()
        flags = widget.textAlignment()
        flags &= ~Qt.AlignVertical_Mask
        flags |= VERTICAL_ALIGN[align]
        widget.setTextAlignment(flags)

    def set_preferred_size(self, preferred_size):
        size = QSize(*preferred_size)
        if size.isValid():
            self.widget().setSizeHint(size)

