from enthought.traits.api import DelegatesTo

from PySide import QtGui

from ..constants import TabPosition
from .element import Element
from .mixins import GeneralWidgetMixin, ResizeEventMixin, MoveEventMixin


TAB_POSITION_MAP = {TabPosition.DEFAULT: QtGui.QTabWidget.North,
                    TabPosition.TOP: QtGui.QTabWidget.North,
                    TabPosition.BOTTOM: QtGui.QTabWidget.South,
                    TabPosition.LEFT: QtGui.QTabWidget.West,
                    TabPosition.RIGHT: QtGui.QTabWidget.East}


class TabGroupWidget(GeneralWidgetMixin, QtGui.QTabWidget):
    pass 


class TabGroup(Element):

    # The index of the currently shown tab. - Int
    current_index = DelegatesTo('abstract_obj')

    # Whether or not the tabs or movable in the group. - Bool
    movable = DelegatesTo('abstract_obj')
    
    # The list of names (in proper order) for the tabs. - List(Str)
    tab_names = DelegatesTo('abstract_obj')

    # The position of the tab bar relative to the pages, - Enum of TabPosition
    tab_position = DelegatesTo('abstract_obj')

    #--------------------------------------------------------------------------
    # Creation Handler
    #--------------------------------------------------------------------------
    def create_widget(self):
        return TabGroupWidget()

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def init_widget(self):
        super(TabGroup, self).init_widget()
        self.widget.currentChanged.connect(self._on_current_changed)
    
    def init_attributes(self):
        super(TabGroup, self).init_attributes()
        self.init_movable()
        self.init_tab_position()

    def init_movable(self):
        self.widget.setMovable(self.movable)

    def init_tab_position(self):
        q_position = TAB_POSITION_MAP[self.tab_position]
        self.widget.setTabPosition(q_position)

    def init_current_index(self):
        # This must be called *after* init layout so that we 
        # actually have some tabs in the container
        self.widget.setCurrentIndex(self.current_index)
    
    def init_layout(self):
        # Overridden from Element because we need to add the children
        # to ourselves in a special way.
        children = self.abstract_obj.children
        tab_names = self.tab_names

        for child in children:
            tab_name = tab_names.get(child, '')
            self.widget.addTab(child.toolkit_obj.widget, tab_name)
        
        # After we add the tab pages, we can init the index
        self.init_current_index()

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def _layout_changed(self):
        # Ignore layout changes on tab groups
        pass

    def _current_index_changed(self):
        self.widget.setCurrentIndex(self.current_index)

    def _movable_changed(self):
        self.widget.setMovable(self.movable)
    
    def _tab_names_changed(self):
        for child, name in self.tab_names.iteritems():
            child_widget = child.toolkit_obj.widget
            idx = self.widget.indexOf(child_widget)
            if idx != -1:
                self.widget.setTabText(idx, name)

    def _tab_position_changed(self):
        q_position = TAB_POSITION_MAP[self.tab_position]
        self.widget.setTabPosition(q_position)
    
    #--------------------------------------------------------------------------
    # Slots
    #--------------------------------------------------------------------------
    def _on_current_changed(self):
        self.current_index = self.widget.currentIndex()


