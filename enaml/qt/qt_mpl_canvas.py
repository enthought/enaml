from .qt.QtGui import QFrame, QVBoxLayout, QCursor, QApplication
from .qt.QtCore import Qt
from .qt import qt_api
from .qt_control import QtControl

import matplotlib
# We want matplotlib to use a Qt4 backend
matplotlib.use('Qt4Agg')
if qt_api == 'pyside':
    matplotlib.rcParams['backend.qt4'] = 'PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg
from matplotlib.backends.backend_qt4 import cursord


class QtMPLCanvas(QtControl):
    """ A Qt implementation of an Enaml MPLCanvas.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying mpl_canvas widget.

        """
        return QFrame(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtMPLCanvas, self).create(tree)
        self.figure = tree['figure']

    def init_layout(self):
        """ A method that allows widgets to do layout initialization.

        This method is called after all widgets in a tree have had
        their 'create' method called. It is useful for doing any
        initialization related to layout.
        """
        super(QtMPLCanvas, self).init_layout()
        figure = self.figure
        widget = self.widget()
        if not figure.canvas:
            canvas = FigureCanvasQTAgg(figure)
        else:
            canvas = figure.canvas
        canvas.setParent(widget)
        if not hasattr(canvas, 'toolbar'):
            toolbar = NavigationToolbar2QTAgg(canvas, canvas)
        else:
            toolbar = canvas.toolbar
        # override the set_cursor method for Pyside support
        # see monkey patch below
        toolbar.set_cursor = lambda cursor: set_cursor(toolbar, cursor)
        vbox = QVBoxLayout()
        vbox.addWidget(canvas)
        vbox.addWidget(toolbar)
        widget.setLayout(vbox)
        widget.setMinimumSize(widget.sizeHint())
        self.size_hint_updated()
        # allow Matplotlib canvas keyboard events
        widget.setFocusPolicy(Qt.ClickFocus)
        widget.setFocus()

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_figure(self, content):
        """ Handle the 'set_figure' action from the Enaml widget.

        """
        raise NotImplementedError


def set_cursor(toolbar, cursor):
    '''Monkey patch for NavigationToolbar Pyside support

    Original method throws segmentation fault
    '''
    QApplication.restoreOverrideCursor()
    qcursor = QCursor()
    qcursor.setShape(cursord[cursor])
    QApplication.setOverrideCursor(qcursor)

