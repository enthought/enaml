#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from weakref import WeakKeyDictionary

from .qt.QtGui import QTabWidget, QTabBar, QResizeEvent, QApplication
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
    """ A custom QTabWidget which handles children of type QPage.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a QNotebook.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to create
            a QTabWidget.

        """
        super(QNotebook, self).__init__(*args, **kwargs)
        self.tabCloseRequested.connect(self.onTabCloseRequested)
        self._hidden_pages = WeakKeyDictionary()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _refreshTabBar(self):
        """ Trigger an immediate relayout and refresh of the tab bar.

        """
        # The public QTabBar api does not provide a way to trigger the
        # 'layoutTabs' method of QTabBarPrivate and there are certain
        # operations (such as modifying a tab close button) which need
        # to have that happen. This method provides a workaround by
        # sending a dummy resize event to the tab bar, followed by one
        # to the tab widget.
        app = QApplication.instance()
        if app is not None:
            bar = self.tabBar()
            size = bar.size()
            event = QResizeEvent(size, size)
            app.sendEvent(bar, event)
            size = self.size()
            event = QResizeEvent(size, size)
            app.sendEvent(self, event)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def onTabCloseRequested(self, index):
        """ The handler for the 'tabCloseRequested' signal.

        """
        self.widget(index).requestClose()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def showPage(self, page):
        """ Show a hidden QPage instance in the notebook.

        If the page is not owned by the notebook, this is a no-op.

        Parameters
        ----------
        page : QPage
            The hidden QPage instance to show in the notebook.

        """
        index = self.indexOf(page)
        if index == -1:
            index = self._hidden_pages.pop(page, -1)
            if index != -1:
                self.insertPage(index, page)

    def hidePage(self, page):
        """ Hide the given QPage instance in the notebook.

        If the page is not owned by the notebook, this is a no-op.

        Parameters
        ----------
        page : QPage
            The QPage instance to hide in the notebook.

        """
        index = self.indexOf(page)
        if index != -1:
            self.removeTab(index)
            page.hide()
            self._hidden_pages[page] = index

    def addPage(self, page):
        """ Add a QPage instance to the notebook. 

        This method should be used in favor of the 'addTab' method.

        Parameters
        ----------
        page : QPage
            The QPage instance to add to the notebook.

        """
        if page.isOpen():
            self.addTab(page, page.title())
            index = self.indexOf(page)
            self.setTabEnabled(index, page.isTabEnabled())
            self.setTabCloseButtonVisible(index, page.isClosable())
        else:
            page.hide()
            self._hidden_pages[page] = self.count()

    def insertPage(self, index, page):
        """ Insert a QPage instance into the notebook.

        This should be used in favor of the 'insertTab' method.

        Parameters
        ----------
        index : int
            The index at which to insert the page.

        page : QPage
            The QPage instance to add to the notebook.

        """
        if page.isOpen():
            index = min(index, self.count())
            self.insertTab(index, page, page.title())
            self.setTabEnabled(index, page.isTabEnabled())
            self.setTabCloseButtonVisible(index, page.isClosable())
        else:
            page.hide()
            self._hidden_pages[page] = index

    def setTabCloseButtonVisible(self, index, visible, refresh=True):
        """ Set whether the close button for the given tab is visible.

        The 'tabsClosable' property must be set to True for this to
        have effect.

        Parameters
        ----------
        index : int
            The index of the target page.

        visible : bool
            Whether or not the close button for the tab should be
            visible.

        refresh : bool, optional
            Whether or not to refresh the tab bar at the end of the
            operation. The default is True.

        """
        # When changing the visibility of a button, we also change its
        # size so that the tab can layout properly.
        if index >= 0 and index < self.count():
            tabBar = self.tabBar()
            btn1 = tabBar.tabButton(index, QTabBar.LeftSide)
            btn2 = tabBar.tabButton(index, QTabBar.RightSide)
            if btn1 is not None:
                btn1.setVisible(visible)
                if not visible:
                    btn1.resize(0, 0)
                else:
                    btn1.resize(btn1.sizeHint())
            if btn2 is not None:
                btn2.setVisible(visible)
                if not visible:
                    btn2.resize(0, 0)
                else:
                    btn2.resize(btn2.sizeHint())
            if refresh:
                self._refreshTabBar()

    def setTabsClosable(self, closable):
        """ Set the tab closable state for the widget.

        This is an overridden parent class method which extends the
        logic to account for the closable state on the individual
        pages.

        Parameters
        ----------
        closable : bool
            Whether or not the tabs should be closable.

        """
        super(QNotebook, self).setTabsClosable(closable)
        # When setting tabs closable to False, the default logic of
        # QTabBar is to delete the close button on the tab. When the
        # closable flag is set to True a new close button is created
        # for every tab, unless one has already been provided. This
        # means we need to make an extra pass over each tab to sync
        # the state of the buttons when the flag is set to True.
        if closable:
            setVisible = self.setTabCloseButtonVisible
            for index in xrange(self.count()):
                page = self.widget(index)
                setVisible(index, page.isClosable(), refresh=False)
        self._refreshTabBar()


class QtNotebook(QtConstraintsWidget):
    """ A Qt implementation of an Enaml Notebook.

    """
    #: Storage for the widget ids of the notebook pages.
    _page_ids = []

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying notebook widget.

        """
        return QNotebook(parent)

    def create(self, tree):
        """ Create and initialize the underyling widget.

        """
        super(QtNotebook, self).create(tree)
        self.set_page_ids(tree['page_ids'])
        self.set_tab_style(tree['tab_style'])
        self.set_tab_position(tree['tab_position'])
        self.set_tabs_closable(tree['tabs_closable'])
        self.set_tabs_movable(tree['tabs_movable'])

    def init_layout(self):
        """ Handle the layout initialization for the notebook.

        """
        super(QtNotebook, self).init_layout()
        widget = self.widget()
        find_child = self.find_child
        for page_id in self._page_ids:
            child = find_child(page_id)
            if child is not None:
                widget.addPage(child.widget())

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_tab_style(self, content):
        """ Handle the 'set_tab_style' action from the Enaml widget.

        """
        self.set_tab_style(content['tab_style'])

    def on_action_set_tab_position(self, content):
        """ Handle the 'set_tab_position' action from the Enaml widget.

        """
        self.set_tab_position(content['tab_position'])

    def on_action_set_tabs_closable(self, content):
        """ Handle the 'set_tabs_closable' action from the Enaml widget.

        """
        self.set_tabs_closable(content['tabs_closable'])

    def on_action_set_tabs_movable(self, content):
        """ Handle the 'set_tabs_movable' action from the Enaml widget.

        """
        self.set_tabs_movable(content['tabs_movable'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_page_ids(self, page_ids):
        """ Set the page ids for the underlying widget.

        """
        self._page_ids = page_ids

    def set_tab_style(self, style):
        """ Set the tab style for the tab bar in the widget.

        """
        self.widget().setDocumentMode(DOCUMENT_MODES[style])

    def set_tab_position(self, position):
        """ Set the position of the tab bar in the widget.

        """
        self.widget().setTabPosition(TAB_POSITIONS[position])

    def set_tabs_closable(self, closable):
        """ Set whether or not the tabs are closable.

        """
        self.widget().setTabsClosable(closable)

    def set_tabs_movable(self, movable):
        """ Set whether or not the tabs are movable.

        """
        self.widget().setMovable(movable)

