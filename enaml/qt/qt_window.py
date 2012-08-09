#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import QSize
from .qt.QtGui import QFrame, QLayout
from .qt_widget_component import QtWidgetComponent


class QWindowLayout(QLayout):
    """ A QLayout subclass which can have at most one layout item. This
    layout item is expanded to fit the allowable space, regardless of 
    its size policy settings. This is similar to how central widgets 
    behave in a QMainWindow.

    The class is designed for use by QWindow other uses are at the 
    user's own risk.

    """
    def __init__(self, *args, **kwargs):
        super(QWindowLayout, self).__init__(*args, **kwargs)
        self._layout_item = None
        self._size_hint = QSize()

    def addItem(self, item):
        """ A virtual method implementation which sets the layout item
        in the layout. Any old item will be overridden.

        """
        self._layout_item = item
        self.update()

    def count(self):
        """ A virtual method implementation which returns 0 if no layout
        item is supplied, or 1 if there is a current layout item.

        """
        return 0 if self._layout_item is None else 1

    def itemAt(self, idx):
        """ A virtual method implementation which returns the layout item 
        for the given index or None if one does not exist.

        """
        if idx == 0:
            return self._layout_item

    def takeAt(self, idx):
        """ A virtual method implementation which removes and returns the
        item at the given index or None if one does not exist.

        """
        if idx == 0:
            res = self._layout_item
            self._layout_item = None
            return res
    
    def sizeHint(self):
        """ A virtual method implementation which returns an invalid
        size hint for the top-level Window.

        """
        return self._size_hint

    def setGeometry(self, rect):
        """ A reimplemented method which sets the geometry of the managed
        widget to fill the given rect.

        """
        super(QWindowLayout, self).setGeometry(rect)
        item = self._layout_item
        if item is not None:
            item.widget().setGeometry(rect)

    def minimumSize(self):
        """ A reimplemented method which returns the minimum size hint
        of the layout item widget as the minimum size of the window.

        """
        parent = self.parentWidget()
        if parent is None:
            return super(QWindowLayout, self).minimumSize()

        expl_size = parent.explicitMinimumSize()
        if expl_size.isValid():
            return expl_size

        item = self._layout_item
        if item is None:
            return parent.minimumSize()

        return item.widget().minimumSizeHint()
            
    def maximumSize(self):
        """ A reimplemented method which returns the minimum size hint
        of the layout item widget as the minimum size of the window.

        """
        parent = self.parentWidget()
        if parent is None:
            return super(QWindowLayout, self).maximumSize()

        expl_size = parent.explicitMaximumSize()
        if expl_size.isValid():
            return expl_size

        item = self._layout_item
        if item is None:
            return parent.maximumSize()

        return item.widget().maximumSize()


class QWindow(QFrame):
    """ A custom QFrame which uses a QWindowLayout to manage its
    central widget.

    The window layout computes the min/max size of the window based
    on its central widget, unless the user explicitly changes them.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a QWindow.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments necessary to 
            initialize a QFrame.

        """
        super(QWindow, self).__init__(*args, **kwargs)
        layout = QWindowLayout()
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)
        self._central_widget = None
        self._expl_min_size = QSize()
        self._expl_max_size = QSize()

    def centralWidget(self):
        """ Returns the central widget for the window.

        Returns
        -------
        result : QWidget or None
            The central widget of the window, or None if no widget
            was provided.

        """
        return self._central_widget

    def setCentralWidget(self, widget):
        """ Set the central widget for this window.

        Parameters
        ----------
        widget : QWidget
            The widget to use as the content of the window.

        """
        self.layout().removeWidget(self._central_widget)
        self._central_widget = widget
        self.layout().addWidget(widget)

    def explicitMinimumSize(self):
        """ Return the explicit minimum size for this widget.

        Returns
        -------
        result : QSize
            If the user has explitly set the minimum size of the 
            widget, that size will be returned. Otherwise, an 
            invalid QSize will be returned.

        """
        return self._expl_min_size

    def explicitMaximumSize(self):
        """ Return the explicit maximum size for this widget.

        Returns
        -------
        result : QSize
            If the user has explitly set the maximum size of the 
            widget, that size will be returned. Otherwise, an 
            invalid QSize will be returned.

        """
        return self._expl_max_size

    def setMinimumSize(self, size):
        """ Set the minimum size for the QWindow.

        This is an overridden parent class method which stores the
        provided size as the explictly set QSize. The explicit 
        size can be reset by passing a QSize of (0, 0).

        Parameters
        ----------
        size : QSize
            The minimum size for the QWindow.

        """
        super(QWindow, self).setMinimumSize(size)
        if size == QSize(0, 0):
            self._expl_min_size = QSize()
        else:
            self._expl_min_size = size 
        self.layout().update()

    def setMaximumSize(self, size):
        """ Set the maximum size for the QWindow.

        This is an overridden parent class method which stores the
        provided size as the explictly set QSize. The explicit 
        size can be reset by passing a QSize equal to the maximum
        widget size of QSize(16777215, 16777215).

        Parameters
        ----------
        size : QSize
            The maximum size for the QWindow.

        """
        super(QWindow, self).setMaximumSize(size)
        if size == QSize(16777215, 16777215):
            self._expl_max_size = QSize()
        else:
            self._expl_max_size = size
        self.layout().update()


class QtWindow(QtWidgetComponent):
    """ A Qt4 implementation of an Enaml Window.

    """
    def create(self):
        """ Create the underlying QWidget object.

        """
        self.widget = QWindow(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the widget's attributes.

        """
        super(QtWindow, self).initialize(attrs)
        self.set_title(attrs['title'])
        self.set_initial_size(attrs['initial_size'])

    def post_initialize(self):
        """ Perform the post initialization work.

        This method sets the central widget for the window.

        """
        super(QtWindow, self).post_initialize()
        children = self.children
        if children:
            self.widget.setCentralWidget(children[0].widget)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_close(self, content):
        """ Handle the 'close' action from the Enaml widget. 

        """
        self.close()

    def on_action_maximize(self, content):
        """ Handle the 'maximize' action from the Enaml widget. 

        """
        self.maximize()

    def on_action_minimize(self, content):
        """ Handle the 'minimize' action from the Enaml widget. 

        """
        self.minimize()

    def on_action_restore(self, content):
        """ Handle the 'restore' action from the Enaml widget. 

        """
        self.restore()

    def on_action_set_icon(self, content):
        """ Handle the 'set-icon' action from the Enaml widget. 

        """
        pass

    def on_action_set_title(self, content):
        """ Handle the 'set-title' action from the Enaml widget. 

        """
        self.set_title(content['title'])
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def close(self):
        """ Close the window

        """
        self.widget.close()

    def maximize(self):
        """ Maximize the window.

        """
        self.widget.showMaximized()

    def minimize(self):
        """ Minimize the window.

        """
        self.widget.showMinimized()

    def restore(self):
        """ Restore the window after a minimize or maximize.

        """
        self.widget.showNormal()

    def set_icon(self, icon):
        """ Set the window icon.

        """
        pass 

    def set_title(self, title):
        """ Set the title of the window.

        """
        self.widget.setWindowTitle(title)

    def set_initial_size(self, size):
        """ Set the initial size of the window.

        """
        if -1 in size:
            return
        self.widget.resize(QSize(*size))

