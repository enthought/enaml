import weakref

from enthought.traits.api import (Any, DelegatesTo, HasStrictTraits, Instance,
                                  on_trait_change)

from PySide import QtCore, QtGui
from PySide.QtGui import QSizePolicy

from ..constants import Color, Layout, SizePolicy
from .abstract_item import AbstractItem
from .mixins import GeneralWidgetMixin


POLICY_MAP = {SizePolicy.FIXED: QSizePolicy.Fixed,
              SizePolicy.MINIMUM: QSizePolicy.Minimum,
              SizePolicy.MAXIMUM: QSizePolicy.Maximum,
              SizePolicy.PREFERRED: QSizePolicy.Preferred,
              SizePolicy.EXPANDING: QSizePolicy.Expanding,
              SizePolicy.MINIMUM_EXPANDING: QSizePolicy.MinimumExpanding,
              SizePolicy.IGNORED: QSizePolicy.Ignored}


LAYOUT_MAP = {Layout.DEFAULT: None,
              Layout.HORIZONTAL: QtGui.QHBoxLayout,
              Layout.VERTICAL: QtGui.QVBoxLayout,
              Layout.FORM: QtGui.QFormLayout,
              Layout.ABSOLUTE: None}


class ElementWidget(GeneralWidgetMixin, QtGui.QWidget):
    pass
    

class Element(AbstractItem):
    
    # The bgcolor of the label - Tuple(float, float, float, float)
    bgcolor = DelegatesTo('abstract_obj')

    # The default palette object. Will be set when widget is created.
    default_palette = Any

    # Default size policy. Will be set when the widget is created.
    default_size_policy = Any

    # Whether the widget is enabled - Bool
    enabled = DelegatesTo('abstract_obj')

    # The font object assigned to the widget
    #font = DelegatesTo('abstract_obj')
    
    # The height of the widget - Int
    height = DelegatesTo('abstract_obj')

    # The layout direction of the children - Enum of Layout values
    layout = DelegatesTo('abstract_obj')

    # The (x, y) position of the widget in its parent - (Int, Int)
    pos = DelegatesTo('abstract_obj')
    
    # The (width, height) size of the widget - (Int, Int)
    size = DelegatesTo('abstract_obj')
    
    # The size hint of the widget - (Int, Int)
    size_hint = DelegatesTo('abstract_obj')
    
    # The size policy of the widget - (SizePolicy, SizePolicy)
    size_policy = DelegatesTo('abstract_obj')

    # Whether the widget is visible - Bool
    visible = DelegatesTo('abstract_obj')
    
    # The width of the widget - Int
    width = DelegatesTo('abstract_obj')
    
    # The X position of the widget - Int
    x = DelegatesTo('abstract_obj')

    # The Y position of the widget
    y = DelegatesTo('abstract_obj')
    
    #--------------------------------------------------------------------------
    # Creation Handler
    #--------------------------------------------------------------------------
    def create_widget(self):
        return ElementWidget()
    
    #--------------------------------------------------------------------------
    # Layout Handler
    #--------------------------------------------------------------------------
    def layout_children(self):
        # If there is a layout already set on the widget, we need
        # to force the deletion immediately, because Qt won't allow
        # us to set a new layout until the old one is deleted.
        old_layout = self.widget.layout()
        if old_layout is not None:
            old_layout.deleteLater()
            evt = QtCore.QEvent.DeferredDelete
            QtGui.QApplication.instance().sendPostedEvents(old_layout, evt)
            del old_layout

        layout_cls = LAYOUT_MAP[self.layout]
        if layout_cls:
            layout = layout_cls()
            if self.layout == Layout.FORM:
                children = self.abstract_obj.children
                while children:
                    row, children = children[:2], children[2:]
                    layout.addRow(*(child.toolkit_obj.widget for child in row))
            else:
                for child in self.abstract_obj.children:
                    layout.addWidget(child.toolkit_obj.widget)
            self.widget.setLayout(layout)
            # Calling activate forces the layout to refresh.
            layout.activate()

        # If we don't have a layout class, that means that we are
        # using either Layout.DEFAULT or Layout.ABSOLUTE. In both
        # cases, we need to parent the child widgets directly
        # since they aren't being managed by a layout.
        else:
            for child in self.abstract_obj.children:
                child.toolkit_obj.widget.setParent(self.widget)
        
    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def init_widget(self):
        self.widget = self.create_widget()
        self.widget.resized.connect(self._on_resized)
        self.widget.moved.connect(self._on_moved)

        # These defaults will be used to restore original values
        # if they are ever changed back to enum.DEFAULT
        self.default_size_policy = self.widget.sizePolicy()
        self.default_palette = self.widget.palette()

    def init_attributes(self):
        self.init_bgcolor()
        self.init_size_policy()
        self.init_size_hint()
        self.init_size()
        self.init_pos()
        self.init_enabled()
        self.init_visible()
    
    def init_layout(self):
        self.layout_children()

    def init_bgcolor(self):
        color = self.bgcolor
        if color != Color.DEFAULT:
            self.widget.setAutoFillBackground(True)
            palette = QtGui.QPalette(self.default_palette)
            qcolor = QtGui.QColor()
            qcolor.setRgbF(*color)
            role = self.widget.backgroundRole()
            palette.setColor(role, qcolor)
            self.widget.setPalette(palette)

    def init_size_policy(self):
        h_policy, v_policy = self.size_policy

        if h_policy == SizePolicy.DEFAULT:
            h_policy = self.default_size_policy.horizontalPolicy()
        else:
            h_policy = POLICY_MAP[h_policy]

        if v_policy == SizePolicy.DEFAULT:
            v_policy = self.default_size_policy.verticalPolicy()
        else:
            v_policy = POLICY_MAP[v_policy]

        self.widget.setSizePolicy(QSizePolicy(h_policy, v_policy))
        self.widget.updateGeometry()

    def init_size_hint(self):
        self.widget.size_hint = self.size_hint

    def init_size(self):
        curr_width = self.widget.width()
        curr_height = self.widget.height()
        width, height = self.size

        if width == -1:
            width = curr_width

        if height == -1:
            height = curr_height

        self.widget.resize(width, height)

    def init_pos(self):
        curr_x = self.widget.x()
        curr_y = self.widget.y()
        x, y = self.pos
        if x == -1:
            x = curr_x
        if y == -1:
            y = curr_y
        self.widget.move(x, y)

    def init_enabled(self):
        self.widget.setEnabled(self.enabled)

    def init_visible(self):
        # We only set the visible value of the widget if the value
        # is False. Otherwise, it would cause the widget to display
        # to the screen prematurely. In Qt, setting visible
        # to True is the same as calling .show(). The exception is 
        # for child widgets, which will never be shown unless they
        # are visible AND their parent is visible. But, since we 
        # have no way of knowing whether or not we are the root
        # widget (without some unnecessary effort) and since the 
        # defualt visibility of child widgets is True, we just
        # need those visibilities which are specified as False.
        if not self.visible:
            self.widget.setVisible(self.visible)

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def _widget_changed(self):
        # XXX how do we/do we want to handle swapping out widgets???
        pass

    def _layout_changed(self):
        self.layout_children()

    def _bgcolor_changed(self):
        color = self.bgcolor
        if color == Color.DEFAULT:
            self.widget.setAutoFillBackground(False)
            self.widget.setPalette(self.default_palette)
        else:
            self.widget.setAutoFillBackground(True)
            palette = QtGui.QPalette(self.default_palette)
            qcolor = QtGui.QColor()
            qcolor.setRgbF(*color)
            role = self.widget.backgroundRole()
            palette.setColor(role, qcolor)
            self.widget.setPalette(palette)

    def _enabled_changed(self):
        self.widget.setEnabled(self.enabled)

    # The x and y traits are synced with pos, 
    # so we don't need handlers for those.
    def _pos_changed(self):
        x, y = self.pos
        self.widget.move(x, y)
        
    # The width and height traits are synced with size,
    # so we don't need handlers for those.
    def _size_changed(self):
        w, h = self.size
        self.widget.resize(w, h)

    def _size_hint_changed(self):
        self.widget.size_hint = self.size_hint
    
    def _size_policy_changed(self):
        # The init_size_policy method does what we want.
        self.init_size_policy()

    def _visible_changed(self):
        self.widget.setVisible(self.visible)
    
    #--------------------------------------------------------------------------
    # Slots
    #--------------------------------------------------------------------------
    @QtCore.Slot(QtCore.QEvent)
    def _on_moved(self, event):
        widget = self.widget
        self.pos = (widget.x(), widget.y())
        
    @QtCore.Slot(QtCore.QEvent)
    def _on_resized(self, event):
        widget = self.widget
        self.size = (widget.width(), widget.height())
    

