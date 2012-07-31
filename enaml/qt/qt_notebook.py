#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Signal
from .qt.QtGui import QTabWidget
from .qt_constraints_widget import QtConstraintsWidget


TAB_POSITIONS = {
    'top': QTabWidget.North,
    'bottom': QTabWidget.South,
    'left': QTabWidget.West,
    'right': QTabWidget.East,
}


DOCUMENT_MODES = {
    'document': True,
    'preferences': False,
}


class QNotebook(QTabWidget):
    """ A custom QTabWidget which behaves like a notebook holding
    instances of QPage.

    """
    #: A signal emitted when the user clicks on the tab close button
    #: for a QPage which is marked as closable. User code should
    #: connect to this signal as opposed to the 'tabCloseRequested'
    #: signal on the parent, since this signal will not be emitted
    #: for QPage instances which are not closable.
    pageCloseRequested = Signal(int)

    def __init__(self, *args, **kwargs):
        """ Initialize a QNotebook.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a QTabWidget.

        """
        super(QNotebook, self).__init__(*args, **kwargs)
        self.tabCloseRequested.connect(self._onTabCloseRequested)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _bind(self, page):
        """ Bind the signal handlers for the given page.

        """
        page.tabTitleChanged.connect(self._onTabTitleChanged)
        page.tabToolTipChanged.connect(self._onTabToolTipChanged)
        page.tabEnabledChanged.connect(self._onTabEnabledChanged)

    def _unbind(self, page):
        """ Unbind the signal handlers for the given page.

        """
        page.tabTitleChanged.disconnect(self._onTabTitleChanged)
        page.tabToolTipChanged.disconnect(self._onTabToolTipChanged)
        page.tabEnabledChanged.disconnect(self._onTabEnabledChanged)

    def _onTabCloseRequested(self, index):
        """ The handler for the 'tabCloseRequested' signal.

        """
        page = self.widget(index)
        if page.tabClosable():
            self.pageCloseRequested.emit(index)

    def _onTabTitleChanged(self, page, title):
        """ The handler for the 'tabTitleChanged' signal on a child
        QPage.

        """
        idx = self.indexOf(page)
        if idx != -1:
            self.setTabText(idx, title)

    def _onTabToolTipChanged(self, page, tool_tip):
        """ The handler for the 'tabToolTipChanged' signal on a child
        QPage.

        """
        idx = self.indexOf(page)
        if idx != -1:
            self.setTabToolTip(idx, tool_tip)

    def _onTabEnabledChanged(self, page, enabled):
        """ The handler for the 'tabEnabledChanged' signal on a child
        QPage.

        """
        idx = self.indexOf(page)
        if idx != -1:
            self.setTabEnabled(idx, enabled)
            page.restoreEnabled()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def addPage(self, page):
        """ Add a QPage instance to the notebook. This method should
        be used in favor of the 'addTab' method of the parent class.

        Parameters
        ----------
        page : QPage
            The QPage instance to add to the notebook.

        """
        idx = self.indexOf(page)
        if idx == -1:
            idx = self.addTab(page, page.tabTitle())
        self.setTabToolTip(idx, page.tabToolTip())
        self.setTabEnabled(idx, page.tabEnabled())
        page.restoreEnabled()
        self._bind(page)

    def removePage(self, index):
        """ Remove the page at the given index. This method should be
        used in favor of the 'removeTab' method of the parent class.

        Parameters
        ----------
        index : int
            The index of the page to remove from the notebook.

        """
        page = self.widget(index)
        if page is not None:
            self.removeTab(index)
            self._unbind(page)


class QtNotebook(QtConstraintsWidget):
    """ A Qt4 implementation of an Enaml Notebook.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Create the underlying widget.

        """
        self.widget = QNotebook(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the widget attributes

        """
        super(QtNotebook, self).initialize(attrs)
        self.set_tab_position(attrs['tab_position'])
        self.set_tab_style(attrs['tab_style'])
        self.set_tabs_closable(attrs['tabs_closable'])
        self.set_tabs_movable(attrs['tabs_movable'])
        self.widget.pageCloseRequested.connect(self.on_page_close_requested)

    def post_initialize(self):
        """ Handle the post initialization for the notebook.

        This method explicitly adds the child QPage instances to the
        underlying QNotebook control.

        """
        super(QtNotebook, self).post_initialize()
        widget = self.widget
        for child in self.children:
            widget.addPage(child.widget)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_tab_position(self, content):
        """ Handle the 'set_tab_position' action from the Enaml widget.

        """
        self.set_tab_position(content['tab_position'])
        
    def on_action_set_tab_style(self, content):
        """ Handle the 'set_tab_style' action from the Enaml widget.

        """
        self.set_tab_style(content['tab_style'])

    def on_action_set_tabs_closable(self, content):
        """ Handle the 'set_tabs_closable' action from the Enaml widget.

        """
        self.set_tabs_closable(content['tabs_closable'])

    def on_action_set_tabs_movable(self, content):
        """ Handle the 'set_tabs_movable' action from the Enaml widget.

        """
        self.set_tabs_movable(content['tabs_movable'])

    def on_action_open_tab(self, content):
        """ Handle the 'open_tab' action from the Enaml widget.

        """
        widget_id = content['widget_id']
        for child in self.children:
            if child.widget_id == widget_id:
                self.widget.addPage(child.widget)
                return

    def on_action_close_tab(self, content):
        """ Handle the 'close_tab' action from the Enaml widget.

        """
        widget_id = content['widget_id']
        for child in self.children:
            if child.widget_id == widget_id:
                widget = self.widget
                widget.removePage(widget.indexOf(child.widget))
                return

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_page_close_requested(self, index):
        """ The signal handler for the 'pageCloseRequested' signal.

        """
        page = self.widget.widget(index)
        self.widget.removePage(index)
        for child in self.children:
            if page == child.widget:
                widget_id = child.widget_id
                content = {'widget_id': widget_id}
                self.send_action('tab_closed', content)
                return

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_tab_position(self, position):
        """ Set the position of the tab bar in the widget.

        """
        self.widget.setTabPosition(TAB_POSITIONS[position])

    def set_tab_style(self, style):
        """ Set the tab style for the tab bar in the widget.

        """
        self.widget.setDocumentMode(DOCUMENT_MODES[style])

    def set_tabs_closable(self, closable):
        """ Set whether or not the tabs are closable.

        """
        self.widget.setTabsClosable(closable)

    def set_tabs_movable(self, movable):
        """ Set whether or not the tabs are movable.

        """
        self.widget.setMovable(movable)

