#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from .qt.QtCore import QSize
from .qt.QtGui import QImage, QPixmap
from .qt_resizing_widgets import _resizable
from .qt_constraints_widget import QtConstraintsWidget
from .q_image_view import QImageView

QCanvasWidget = _resizable(QImageView)

class QtRemoteCanvas(QtConstraintsWidget):
    """ A Qt4 wrapper around an image canvas.

    """

    def create_widget(self, parent, tree):
        """ Creates the underlying QCanvasWidget to render the remote canvas

        """
        return QCanvasWidget(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        # Need to create the widget here, since I need access to the component
        super(QtRemoteCanvas, self).create(tree)
        self.widget().resized.connect(self.on_resize)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_canvas(self, content):
        """ Handle the 'set_canvas' action from the Enaml widget.
    
        """
        canvas = content['canvas']
        stride = content['stride']
        data = canvas._data
        w, h = canvas._size
        img = QImage(data, w, h, stride, QImage.Format_ARGB32)
        
        self.widget().setPixmap(QPixmap.fromImage(img))

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_resize(self):
        """ Notify the server when the widget size changes so the canvas can be
        regenerated.

        """
        size = self.widget().size()
        content = {'size': (size.width(), size.height())}
        self.send_action('size_changed', content)


